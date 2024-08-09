async def test_get_one(session, accessibility):
    from eigakan.core.statement import ReadOneBy

    access = await ReadOneBy(
        "id", accessibility.id, model=accessibility.__class__
    )(session)
    assert access.id == accessibility.id


async def test_get_all(session, accessibilities):
    from eigakan.core.statement import ReadAll

    model = accessibilities[0].__class__
    resources = await ReadAll(model)(session)
    assert len(resources) == 2
    assert [acc.id for acc in resources] == [acc.id for acc in accessibilities]


async def test_get_all_filtered(session, accessibilities):
    from eigakan.core.statement import ReadAll
    from eigakan.core.updaters.commons import ScalarUpdater

    model = accessibilities[0].__class__
    resources = await ReadAll(
        model,
        ScalarUpdater(model, "name", accessibilities[-1].name),
    )(session)
    assert len(resources) == 1
    assert resources[0].id == accessibilities[-1].id
