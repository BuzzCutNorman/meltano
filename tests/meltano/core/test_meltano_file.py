from __future__ import annotations

import datetime

import pytest

from meltano.core.meltano_file import MeltanoFile


class TestMeltanoFile:
    @pytest.mark.usefixtures("tap", "target")
    def test_load(self, project) -> None:
        meltano_file = MeltanoFile.parse(project.meltano)
        assert meltano_file

    @pytest.mark.usefixtures("mapper")
    def test_get_plugins_for_mappings(self, project) -> None:
        meltano_file = MeltanoFile.parse(project.meltano)

        test_config = {
            "name": "mapper-mock",
            "variant": "meltano",
            "mappings": [
                {
                    "name": "mock-mapping-0",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "author_email",
                                "tap_stream_name": "commits",
                                "type": "MASK-HIDDEN",
                            },
                        ],
                    },
                },
                {
                    "name": "mock-mapping-1",
                    "config": {
                        "transformations": [
                            {
                                "field_id": "given_name",
                                "tap_stream_name": "users",
                                "type": "lowercase",
                            },
                        ],
                    },
                },
            ],
        }

        plugins = meltano_file.get_plugins_for_mappings(test_config)
        assert len(plugins) == 2

        assert plugins[0].extra_config.get("_mapping")
        assert (
            plugins[0].extra_config.get("_mapping_name")
            == test_config["mappings"][0]["name"]
        )
        assert plugins[0].config == test_config["mappings"][0]["config"]

        assert plugins[1].extra_config.get("_mapping")
        assert (
            plugins[1].extra_config.get("_mapping_name")
            == test_config["mappings"][1]["name"]
        )
        assert plugins[1].config == test_config["mappings"][1]["config"]

    def test_load_env(self) -> None:
        meltano_file = MeltanoFile(
            version=1,
            env={
                "FOO": 1,
                "BAR": datetime.datetime(2025, 5, 20, tzinfo=datetime.timezone.utc),
            },
            plugins={},
            schedules=[],
            environments=[],
            jobs=[],
        )
        assert meltano_file.env["FOO"] == "1"
        assert meltano_file.env["BAR"] == "2025-05-20 00:00:00+00:00"
