from app.infrastructure.command_center.activity_feed import (
    ActivityFeed,
)


class TestActivityFeed:

    def test_agent_started_tracks_active(self):

        feed = ActivityFeed()

        feed.agent_started("rca", task="analyze")

        snapshot = feed.snapshot()

        assert snapshot.active_agents == ["rca"]

        assert snapshot.current_tasks == ["analyze"]

    def test_agent_completed_clears_active_and_counts(self):

        feed = ActivityFeed()

        feed.agent_started("rca")

        feed.agent_completed("rca", success=True)

        snapshot = feed.snapshot()

        assert snapshot.active_agents == []

        assert snapshot.completed_actions == 1

        assert snapshot.failures == 0

    def test_agent_completed_failure_counts_failure(self):

        feed = ActivityFeed()

        feed.agent_started("rca")

        feed.agent_completed("rca", success=False)

        snapshot = feed.snapshot()

        assert snapshot.completed_actions == 0

        assert snapshot.failures == 1

    def test_record_action_increments_counts(self):

        feed = ActivityFeed()

        feed.record_action(True, agent="tool", task="restart")

        feed.record_action(False, agent="tool", task="rollback")

        snapshot = feed.snapshot()

        assert snapshot.completed_actions == 1

        assert snapshot.failures == 1

    def test_multiple_active_agents(self):

        feed = ActivityFeed()

        feed.agent_started("rca", task="analyze")

        feed.agent_started("verifier", task="verify")

        snapshot = feed.snapshot()

        assert set(snapshot.active_agents) == {
            "rca",
            "verifier",
        }

        assert set(snapshot.current_tasks) == {
            "analyze",
            "verify",
        }

    def test_history_records_entries(self):

        feed = ActivityFeed()

        feed.agent_started("rca", task="analyze")

        feed.record_action(True, agent="tool", task="restart")

        feed.record_action(False, agent="tool", task="rollback")

        history = feed.history()

        assert len(history) == 3

        assert history[0].status == "started"

        assert history[-1].status == "failed"

    def test_history_limit(self):

        feed = ActivityFeed()

        for i in range(5):
            feed.record_action(True, agent="tool", task=f"t-{i}")

        assert len(feed.history(limit=2)) == 2

        assert feed.history(limit=2)[-1].task == "t-4"

    def test_clear_resets_state(self):

        feed = ActivityFeed()

        feed.agent_started("rca")

        feed.record_action(True, agent="tool")

        feed.clear()

        snapshot = feed.snapshot()

        assert snapshot.active_agents == []

        assert snapshot.completed_actions == 0

        assert snapshot.failures == 0

        assert feed.history() == []
