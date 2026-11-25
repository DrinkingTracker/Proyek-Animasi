
"""Entry point praktis untuk menjalankan render Scene 6 langsung dari VS Code (Run / F5)."""

from manim import tempconfig

from src.scene6_kabut_asap import Scene6KabutAsap

if __name__ == "__main__":
    # Ubah quality ke "high_quality" (1080p 60fps) atau "production_quality" untuk render final.
    with tempconfig(
        {
            "quality": "medium_quality",  # 720p 30fps cepat untuk preview
            "preview": True,
        }
    ):
        scene = Scene6KabutAsap()
        scene.render()

