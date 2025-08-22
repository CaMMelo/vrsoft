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
