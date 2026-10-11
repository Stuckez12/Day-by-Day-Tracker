import json
import uuid
from datetime import date

import pytest
from sqlalchemy.orm import Session

from src.models import RankerModel
from src.schemas import Metadata
from src.workflows import RangedBackupWorkflow


class TestCreateRangedBackupWorkflow:
    def test_success(
        self,
        test_ranker: RankerModel,
        test_ranged_backup_workflow: RangedBackupWorkflow,
    ):
        test_ranged_backup_workflow.create_ranged_backup()

        assert test_ranged_backup_workflow.backup_file_path
        assert test_ranged_backup_workflow.backup_file_path.is_file()

        with test_ranged_backup_workflow.backup_file_path.open("r") as file:
            data = json.load(file)

        assert data["ranker"][0]["id"] == str(test_ranker.id)
        assert len(test_ranged_backup_workflow.metadata_files) == 1

        assert test_ranged_backup_workflow.metadata_tool
        assert test_ranged_backup_workflow.metadata_tool.name == "dbdt_json_collector"
        assert test_ranged_backup_workflow.metadata_tool.version == "1"

        test_ranged_backup_workflow.backup_file_path.unlink()
        assert not test_ranged_backup_workflow.backup_file_path.exists()


class TestApplyRangedBackupWorkflow:
    def test_success(
        self,
        test_session: Session,
        test_ranker: RankerModel,
        test_metadata_schema: Metadata,
        test_ranged_backup_workflow: RangedBackupWorkflow,
    ):
        create_ranker_uuid = str(uuid.uuid4())
        test_ranged_backup_workflow.metadata = test_metadata_schema
        data = {
            "ranker": [
                {
                    "id": str(test_ranker.id),
                    "ranking": 10,
                    "text_notes": "Applied ranged backup",
                },
                {
                    "id": create_ranker_uuid,
                    "personnel_id": test_ranker.personnel_id,
                    "day": date.today().strftime("%Y-%m-%d"),
                    "ranking": 3,
                    "text_notes": "Applied ranged backup w new row",
                },
            ]
        }

        test_ranged_backup_workflow.apply_ranged_backup_to_database(test_session, data)
        test_session.refresh(test_ranker)

        assert test_ranker.ranking == 10
        assert test_ranker.text_notes == "Applied ranged backup"

        created_rank = (
            test_session.query(RankerModel)
            .filter(RankerModel.id == create_ranker_uuid)
            .one()
        )
        assert created_rank.ranking == 3
        assert created_rank.text_notes == "Applied ranged backup w new row"

        test_session.query(RankerModel).filter(
            RankerModel.id == create_ranker_uuid
        ).delete()
        test_session.commit()


@pytest.mark.skip(reason="TODO when chains have been created between backups")
class TestVerifyRangedBackupWorkflow:
    def test_success(self):
        pass
