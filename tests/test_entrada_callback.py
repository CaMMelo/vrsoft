from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from backend.model import PayloadNotificacao, TipoNotificacao, notificar


@pytest.mark.asyncio
async def test_notificar():
    channel = MagicMock()
    channel.default_exchange.publish = AsyncMock()

    payload = PayloadNotificacao(
        mensagemId=uuid4(),
        conteudoMensagem="Mensagem de teste",
        tipoNotificacao=TipoNotificacao.EMAIL,
    )

    notificacoes = {}

    notificacao = await notificar(payload, channel, notificacoes)

    assert notificacoes[notificacao.traceId] is notificacao
    assert payload.mensagemId == notificacao.mensagemId
    assert payload.conteudoMensagem == notificacao.conteudoMensagem
    assert payload.tipoNotificacao == notificacao.tipoNotificacao
