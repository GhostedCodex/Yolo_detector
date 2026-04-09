import os
import uuid
from flask import Blueprint, render_template, request, jsonify, Response, send_file
from detector import VideoDetector

bp = Blueprint("main", __name__)
detector = VideoDetector()  # loads model once at startup


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/detect", methods=["POST"])
def detect():
    if "video" not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    file = request.files["video"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    job_id = str(uuid.uuid4())[:8]
    input_path = f"uploads/{job_id}_input.mp4"
    output_path = f"uploads/{job_id}_output.mp4"
    file.save(input_path)

    try:
        summary = detector.process_video(input_path, output_path)
        return jsonify({
            "job_id": job_id,
            "frames": summary["frames"],
            "total_detections": sum(len(d["objects"]) for d in summary["detections"]),
            "download_url": f"/download/{job_id}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/download/<job_id>")
def download(job_id):
    path = f"uploads/{job_id}_output.mp4"
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    return send_file(path, mimetype="video/mp4", as_attachment=True,
                     download_name="detected_output.mp4")


@bp.route("/stream")
def stream():
    """MJPEG stream from webcam with live detection."""
    return Response(detector.stream_frames(source=0),
                    mimetype="multipart/x-mixed-replace; boundary=frame")
