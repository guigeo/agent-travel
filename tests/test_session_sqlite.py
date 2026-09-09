from agent_travel.core.session import SqliteSessionStore


def test_sqlite_store_persiste_historico_entre_get(tmp_path):
    store = SqliteSessionStore(tmp_path / "sessions.sqlite", ttl_seconds=3600)
    session = store.get("abc")
    session.messages.append({"role": "user", "content": "oi"})
    store.save("abc", session)

    reloaded = store.get("abc")
    assert reloaded.messages == [{"role": "user", "content": "oi"}]


def test_sqlite_store_expira_sessao_por_ttl(tmp_path, monkeypatch):
    now = {"value": 1_000.0}
    monkeypatch.setattr("agent_travel.core.session.time.time", lambda: now["value"])

    store = SqliteSessionStore(tmp_path / "sessions.sqlite", ttl_seconds=10)
    session = store.get("abc")
    session.messages.append({"role": "user", "content": "oi"})
    store.save("abc", session)

    now["value"] = 1_020.0
    reloaded = store.get("abc")
    assert reloaded.messages == []
