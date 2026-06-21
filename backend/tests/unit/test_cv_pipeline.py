"""Unit tests for CV pipeline stages and runner.

All cv2 / ultralytics / pandas imports are mocked via patch.dict(sys.modules)
so this file runs under `uv sync --dev` (no cv extras required).
"""

from __future__ import annotations

import sys
import uuid
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cv2_mock(fps: float = 25.0, frames: int = 250, w: int = 1920, h: int = 1080) -> MagicMock:
    """Return a cv2 mock whose VideoCapture returns sensible defaults."""
    cap = MagicMock()
    cap.get.side_effect = lambda p: {5: fps, 7: float(frames), 3: float(w), 4: float(h)}.get(p, 0.0)
    cap.read.return_value = (False, None)  # default: no frames
    cv2 = MagicMock()
    cv2.VideoCapture.return_value = cap
    cv2.CAP_PROP_FPS = 5
    cv2.CAP_PROP_FRAME_COUNT = 7
    cv2.CAP_PROP_FRAME_WIDTH = 3
    cv2.CAP_PROP_FRAME_HEIGHT = 4
    return cv2


# ---------------------------------------------------------------------------
# probe stage
# ---------------------------------------------------------------------------


def test_probe_returns_correct_metadata(tmp_path) -> None:
    fake_video = tmp_path / "clip.mp4"
    fake_video.write_bytes(b"fake")

    mock_cv2 = _make_cv2_mock(fps=25.0, frames=250, w=1920, h=1080)

    with patch.dict(sys.modules, {"cv2": mock_cv2}):
        if "pitchmind.pipeline.stages.probe" in sys.modules:
            del sys.modules["pitchmind.pipeline.stages.probe"]
        from pitchmind.pipeline.stages.probe import probe

        result = probe(fake_video)

    assert result.fps == 25.0
    assert result.total_frames == 250
    assert result.width == 1920
    assert result.height == 1080
    assert abs(result.duration_s - 10.0) < 0.01
    mock_cv2.VideoCapture.return_value.release.assert_called_once()


def test_probe_uses_fallback_fps_when_zero(tmp_path) -> None:
    fake_video = tmp_path / "clip.mp4"
    fake_video.write_bytes(b"fake")

    mock_cv2 = _make_cv2_mock(fps=0.0, frames=0, w=0, h=0)

    with patch.dict(sys.modules, {"cv2": mock_cv2}):
        if "pitchmind.pipeline.stages.probe" in sys.modules:
            del sys.modules["pitchmind.pipeline.stages.probe"]
        from pitchmind.pipeline.stages.probe import probe

        result = probe(fake_video)

    assert result.fps == 25.0  # fallback
    assert result.duration_s == 0.0


# ---------------------------------------------------------------------------
# sample stage
# ---------------------------------------------------------------------------


def test_sample_frames_yields_at_correct_step(tmp_path) -> None:
    fake_video = tmp_path / "clip.mp4"
    fake_video.write_bytes(b"fake")

    mock_cv2 = _make_cv2_mock(fps=25.0)
    fake_frame = MagicMock()
    # 50 real frames, then EOF
    mock_cv2.VideoCapture.return_value.read.side_effect = [(True, fake_frame)] * 50 + [
        (False, None)
    ]

    with patch.dict(sys.modules, {"cv2": mock_cv2}):
        if "pitchmind.pipeline.stages.sample" in sys.modules:
            del sys.modules["pitchmind.pipeline.stages.sample"]
        from pitchmind.pipeline.stages.sample import sample_frames

        results = list(sample_frames(fake_video, target_fps=5.0))

    # native 25 fps / 5 target = step 5 → 50 frames / 5 = 10 samples
    assert len(results) == 10
    sample_indices = [r[0] for r in results]
    assert sample_indices == list(range(10))
    # timestamps increase
    assert results[0][1] == pytest.approx(0.0)
    assert results[1][1] == pytest.approx(5 / 25.0)
    mock_cv2.VideoCapture.return_value.release.assert_called_once()


def test_sample_frames_empty_video(tmp_path) -> None:
    fake_video = tmp_path / "empty.mp4"
    fake_video.write_bytes(b"fake")

    mock_cv2 = _make_cv2_mock(fps=25.0)
    mock_cv2.VideoCapture.return_value.read.return_value = (False, None)

    with patch.dict(sys.modules, {"cv2": mock_cv2}):
        if "pitchmind.pipeline.stages.sample" in sys.modules:
            del sys.modules["pitchmind.pipeline.stages.sample"]
        from pitchmind.pipeline.stages.sample import sample_frames

        results = list(sample_frames(fake_video, target_fps=5.0))

    assert results == []


# ---------------------------------------------------------------------------
# detect stage
# ---------------------------------------------------------------------------


def test_detect_batches_correctly_and_flushes_partial() -> None:
    from pitchmind.cv.detectors.base import Detection

    fake_det = Detection(
        frame_idx=0,
        timestamp_s=0.0,
        cls=0,
        cls_name="player",
        conf=0.9,
        x1=0.0,
        y1=0.0,
        x2=100.0,
        y2=100.0,
    )
    mock_detector = MagicMock()
    mock_detector.predict.return_value = [fake_det]

    fake_frame = MagicMock()
    frames_iter = iter([(0, 0.0, fake_frame), (1, 0.1, fake_frame), (2, 0.2, fake_frame)])

    # Use a mock pandas that records the DataFrame constructor call
    mock_pd = MagicMock()
    mock_pd.DataFrame.return_value = MagicMock()

    with patch.dict(sys.modules, {"pandas": mock_pd}):
        if "pitchmind.pipeline.stages.detect" in sys.modules:
            del sys.modules["pitchmind.pipeline.stages.detect"]
        from pitchmind.pipeline.stages.detect import detect

        detect(frames_iter, mock_detector, batch_size=2)

    # batch_size=2: call 1 with frames 0+1, call 2 with frame 2 (partial flush)
    assert mock_detector.predict.call_count == 2
    # DataFrame called with 2 detections (one per predict call)
    rows_arg = mock_pd.DataFrame.call_args[0][0]
    assert len(rows_arg) == 2


def test_detect_returns_empty_frame_on_no_detections() -> None:
    mock_detector = MagicMock()
    mock_detector.predict.return_value = []

    frames_iter = iter([(0, 0.0, MagicMock())])

    mock_pd = MagicMock()
    mock_pd.DataFrame.return_value = MagicMock()

    with patch.dict(sys.modules, {"pandas": mock_pd}):
        if "pitchmind.pipeline.stages.detect" in sys.modules:
            del sys.modules["pitchmind.pipeline.stages.detect"]
        from pitchmind.pipeline.stages.detect import detect

        detect(frames_iter, mock_detector, batch_size=16)

    # No detections → early-return empty DataFrame with explicit columns
    mock_pd.DataFrame.assert_called_once()
    assert "columns" in mock_pd.DataFrame.call_args[1]


# ---------------------------------------------------------------------------
# runner — all sub-imports mocked via sys.modules
# ---------------------------------------------------------------------------


def test_runner_calls_stages_and_updates_db() -> None:
    from pitchmind.pipeline.stages.probe import ProbeResult

    probe_result = ProbeResult(fps=25.0, duration_s=10.0, width=1920, height=1080, total_frames=250)

    fake_df = MagicMock()
    fake_df.__len__ = MagicMock(return_value=5)
    fake_df.empty = False
    # df["frame_idx"].nunique() must return an int so int() doesn't fail
    fake_df.__getitem__ = MagicMock(return_value=MagicMock(nunique=MagicMock(return_value=3)))

    mock_probe_mod = MagicMock()
    mock_probe_mod.probe.return_value = probe_result
    mock_sample_mod = MagicMock()
    mock_sample_mod.sample_frames.return_value = iter([])
    mock_detect_mod = MagicMock()
    mock_detect_mod.detect.return_value = fake_df
    mock_sync_mod = MagicMock()

    extra_mods = {
        "pandas": MagicMock(),
        "pitchmind.pipeline.stages.probe": mock_probe_mod,
        "pitchmind.pipeline.stages.sample": mock_sample_mod,
        "pitchmind.pipeline.stages.detect": mock_detect_mod,
        "pitchmind.cv.detectors.yolov11": MagicMock(),
        "pitchmind.storage.sync_client": mock_sync_mod,
    }

    upload_id = str(uuid.uuid4())
    mock_engine = MagicMock()

    with patch.dict(sys.modules, extra_mods):
        # Clear cached runner so it re-imports with mocked sub-modules active
        sys.modules.pop("pitchmind.pipeline.runner", None)

        with (
            patch("pitchmind.pipeline.runner._get_storage_key", return_value="videos/test.mp4"),
            patch("pitchmind.pipeline.runner._update_duration") as mock_dur,
            patch("pitchmind.pipeline.runner._update_meta") as mock_meta,
        ):
            from pitchmind.pipeline.runner import run_pipeline  # noqa: PLC0415

            run_pipeline(upload_id, mock_engine)

    mock_dur.assert_called_once_with(upload_id, 10.0, mock_engine)

    mock_sync_mod.upload_file_sync.assert_called_once()
    _path, artifact_key, content_type = mock_sync_mod.upload_file_sync.call_args[0]
    assert artifact_key == f"artifacts/{upload_id}/detections.parquet"
    assert content_type == "application/octet-stream"

    mock_meta.assert_called_once()
    meta = mock_meta.call_args[0][1]
    assert meta["cv"]["total_detections"] == 5
    assert meta["cv"]["total_frames_sampled"] == 3
    assert meta["cv"]["artifact_key"] == f"artifacts/{upload_id}/detections.parquet"
