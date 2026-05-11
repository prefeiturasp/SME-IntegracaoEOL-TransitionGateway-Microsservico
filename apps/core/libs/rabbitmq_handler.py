"""Logging handler que publica registros em uma fila RabbitMQ."""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime

import pika
import pika.exceptions


class RabbitMQHandler(logging.Handler):
    """Envia cada log record como mensagem JSON para uma fila RabbitMQ.

    Reconecta automaticamente quando a conexão é perdida.
    Falhas de publicação são silenciadas para não interromper a aplicação.
    Guard de re-entrância por thread evita recursão quando o pika loga.
    """

    def __init__(
        self,
        host: str,
        queue: str,
        username: str,
        password: str,
        virtual_host: str = "/",
        level: int | str = logging.NOTSET,
    ) -> None:
        super().__init__(level)
        self._host = host
        self._queue = queue
        self._virtual_host = virtual_host
        self._credentials = pika.PlainCredentials(username, password)
        self._connection: pika.BlockingConnection | None = None
        self._channel: (
            pika.adapters.blocking_connection.BlockingChannel | None
        ) = None
        self._local = threading.local()

    def _connect(self) -> None:
        params = pika.ConnectionParameters(
            host=self._host,
            virtual_host=self._virtual_host,
            credentials=self._credentials,
            connection_attempts=2,
            retry_delay=1,
            socket_timeout=3,
        )
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=self._queue, durable=True)

    def _ensure_connected(self) -> bool:
        try:
            if self._connection is None or self._connection.is_closed:
                self._connect()
            return True
        except Exception:
            self._connection = None
            self._channel = None
            return False

    def emit(self, record: logging.LogRecord) -> None:
        if getattr(self._local, "in_emit", False):
            return
        self._local.in_emit = True
        try:
            if not self._ensure_connected():
                return
            body = json.dumps(
                {
                    "timestamp": datetime.fromtimestamp(
                        record.created
                    ).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "request_id": getattr(record, "request_id", "-"),
                    "service": getattr(record, "service", "-"),
                    "transaction_id": getattr(record, "transaction_id", "-"),
                    "trace_id": getattr(record, "trace_id", "-"),
                },
                ensure_ascii=False,
            )
            self._channel.basic_publish(  # type: ignore[union-attr]
                exchange="",
                routing_key=self._queue,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent,
                    content_type="application/json",
                ),
            )
        except Exception:
            self._connection = None
            self._channel = None
        finally:
            self._local.in_emit = False
