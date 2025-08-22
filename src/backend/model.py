from dataclasses import dataclass
from enum import Enum, StrEnum
from uuid import UUID

from pydantic import BaseModel


class TipoNotificacao(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class StatusNotificacao(StrEnum):
    RECEBIDO = "RECEBIDO"
    FALHA_PROCESSAMENTO_INICIAL = "FALHA_PROCESSAMENTO_INICIAL"
    PROCESSADO_INTERMEDIARIO = "PROCESSADO_INTERMEDIARIO"
    FALHA_FINAL_PROCESSAMENTO = "FALHA_FINAL_PROCESSAMENTO"
    PROCESSADO_COM_SUCESSO = "PROCESSADO_COM_SUCESSO"
    REPROCESSADO_COM_SUCESSO = "REPROCESSADO_COM_SUCESSO"
    FALHA_ENVIO_FINAL = "FALHA_ENVIO_FINAL"
    ENVIADO_SUCESSO = "ENVIADO_SUCESSO"


class PayloadNotificacao(BaseModel):
    mensagemId: UUID
    conteudoMensagem: str
    tipoNotificacao: TipoNotificacao


@dataclass
class Notificacao:
    traceId: UUID
    mensagemId: UUID
    conteudoMensagem: str
    tipoNotificacao: TipoNotificacao
    statusNotificacao: StatusNotificacao


notificacoes = {}


async def notificar(payload, channel):
    traceId = f"{uuid4()}"
    notificacoes[traceId] = Notificacao(
        traceId=traceId,
        mensagemId=payload.mensagemId,
        conteudoMensagem=payload.conteudoMensagem,
        tipoNotificacao=TipoNotificacao(payload.tipoNotificacao),
        statusNotificacao=StatusNotificacao.RECEBIDO,
    )
    message_body = json.dumps(
        {"content": asdict(notificacoes[traceId])}, default=str
    ).encode()
    await channel.default_exchange.publish(
        aio_pika.Message(body=message_body),
        routing_key="fila.notificacao.entrada.caiomelo",
    )
    return Notificacao
