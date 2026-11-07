import pytest

from triage.handoff import decide
from triage.schemas import ExtractedFields, Team
from triage.schemas import InquiryType as T
from triage.schemas import Priority as P
from triage.schemas import Segment as S


@pytest.mark.parametrize(
    "itype,seg,team,prio",
    [
        (T.machine_trouble, S.dtc, Team.service_desk, P.normal),
        (T.machine_trouble, S.b2b, Team.service_desk, P.high),
        (T.quality_complaint, S.dtc, Team.customer_care, P.normal),
        (T.quality_complaint, S.b2b, Team.quality_team, P.high),
        (T.partner_request, S.b2b, Team.partner_team, P.normal),
        (T.unclear_other, S.dtc, Team.front_desk, P.low),
        (T.unclear_other, S.b2b, Team.front_desk, P.low),
    ],
)
def test_team_and_priority_table(itype, seg, team, prio):
    h = decide(itype, seg, False)
    assert (h.team, h.priority, h.cc) == (team, prio, [])


def test_safety_is_urgent_and_copies_quality():
    h = decide(T.machine_trouble, S.dtc, True)
    assert h.priority == P.urgent and h.cc == [Team.quality_team]
    assert any("stop using" in s for s in h.added_steps)


def test_safety_on_b2b_quality_does_not_copy_itself():
    h = decide(T.quality_complaint, S.b2b, True)
    assert h.team == Team.quality_team and h.cc == []


def test_missing_ids_add_steps():
    h = decide(T.machine_trouble, S.dtc, False, ExtractedFields(model="FH-340"))
    assert h.added_steps == ["Ask the sender for the serial number."]
    h = decide(T.partner_request, S.b2b, False, ExtractedFields())
    assert h.added_steps == []
