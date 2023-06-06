"""OTel utils"""
import asyncio

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http import \
    _log_exporter as LogExporter  # noqa
from opentelemetry.exporter.otlp.proto.http.metric_exporter import \
    OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider  # noqa
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor  # noqa
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from crawlerstack_spiderkeeper_server.config import settings

resource = Resource(attributes={
    SERVICE_NAME: settings.SERVICE_NAME
})


def register_tracer_exporter() -> TracerProvider:
    """Register tracer exporter to tracer_provider"""
    processor = BatchSpanProcessor(OTLPSpanExporter(
        endpoint=settings.EXPORTER_TRACES_ENDPOINT,
    ))
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    trace.get_tracer_provider().add_span_processor(processor)  # noqa
    return provider


def register_meter_exporter() -> MeterProvider:
    """Register meter exporter to meter_provider"""
    reader = PeriodicExportingMetricReader(OTLPMetricExporter(
        endpoint=settings.EXPORTER_METRICS_ENDPOINT,
    ))
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    return provider


def register_log_exporter() -> LoggerProvider:
    """Register log exporter to log_provider"""
    processor = BatchLogRecordProcessor(LogExporter.OTLPLogExporter(
        endpoint=settings.EXPORTER_LOGS_ENDPOINT,
    ))
    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(processor)
    return provider


async def otel_register_app(app: FastAPI) -> None:
    """Register app"""
    FastAPIInstrumentor.instrument_app(app)
    await asyncio.sleep(1)


# 全局变量,导包时完成创建
tracer_provider: TracerProvider = register_tracer_exporter()
meter_provider: MeterProvider = register_meter_exporter()
log_provider: LoggerProvider = register_log_exporter()


async def otel_provider_shutdown():
    """Otel provider shutdown"""
    tracer_provider.shutdown()
    meter_provider.shutdown()
    log_provider.shutdown()
    await asyncio.sleep(1)
