"""
DataHarbour Project - LinkedIn Promotional Video
=================================================
Portrait orientation (1080x1920) for mobile-first LinkedIn engagement.
Silent with animated text overlays.

Render: manim render promo/video.py FullVideo -qh
"""
from manim import *

# Color palette
DARK_BG = "#0f172a"
BLUE_PRIMARY = "#3b82f6"
BLUE_DARK = "#1e40af"
INDIGO = "#6366f1"
CYAN = "#06b6d4"
GREEN = "#10b981"
ORANGE = "#f59e0b"
RED = "#ef4444"
WHITE = "#f8fafc"
GRAY = "#94a3b8"
SLATE = "#334155"

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16
config.background_color = DARK_BG


class TitleScene(Scene):
    """Scene 1: Hook - Title card (5 seconds)"""

    def construct(self):
        # Main title
        title = Text("DataHarbour", font_size=72, color=WHITE, weight=BOLD)
        title.move_to(UP * 2)

        subtitle = Text("Project (DHP)", font_size=42, color=BLUE_PRIMARY)
        subtitle.next_to(title, DOWN, buff=0.3)

        # Tagline
        tagline = Text(
            "A Complete Data Lakehouse\nPlatform from Scratch",
            font_size=32,
            color=GRAY,
            line_spacing=1.2,
        )
        tagline.next_to(subtitle, DOWN, buff=1.0)

        # Tech badges
        techs = ["Python", "FastAPI", "Spark", "Kafka", "K8s"]
        badges = VGroup()
        for tech in techs:
            badge = VGroup(
                RoundedRectangle(
                    width=1.8, height=0.6, corner_radius=0.2,
                    fill_color=SLATE, fill_opacity=1, stroke_color=BLUE_PRIMARY, stroke_width=1
                ),
                Text(tech, font_size=20, color=CYAN),
            )
            badge[1].move_to(badge[0].get_center())
            badges.add(badge)
        badges.arrange_in_grid(rows=2, cols=3, buff=0.3)
        badges.next_to(tagline, DOWN, buff=1.2)

        # Animate
        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.play(FadeIn(tagline, shift=UP * 0.3), run_time=0.7)
        self.play(
            LaggedStart(*[GrowFromCenter(b) for b in badges], lag_ratio=0.15),
            run_time=1.2,
        )
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


class ProblemScene(Scene):
    """Scene 2: The Problem (10 seconds)"""

    def construct(self):
        # Header
        header = Text("The Problem", font_size=48, color=RED, weight=BOLD)
        header.move_to(UP * 6)
        self.play(FadeIn(header, shift=DOWN * 0.3), run_time=0.5)

        # Pain points appearing one by one
        problems = [
            "Manual Spark job management",
            "No retry logic on failures",
            "Scattered logs everywhere",
            "Zero observability",
            "No metadata governance",
        ]

        pain_group = VGroup()
        for i, problem in enumerate(problems):
            cross = Text("✗", font_size=36, color=RED)
            text = Text(problem, font_size=28, color=WHITE)
            row = VGroup(cross, text).arrange(RIGHT, buff=0.3)
            pain_group.add(row)

        pain_group.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        pain_group.move_to(UP * 1.5)

        for row in pain_group:
            self.play(FadeIn(row, shift=LEFT * 0.5), run_time=0.4)

        self.wait(1.0)

        # Transition
        solution_text = Text(
            "There's a better way →",
            font_size=36, color=GREEN, weight=BOLD,
        )
        solution_text.move_to(DOWN * 4)
        self.play(FadeIn(solution_text, shift=UP * 0.5), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)


class ArchitectureScene(Scene):
    """Scene 3: Architecture building up (25 seconds)"""

    def construct(self):
        header = Text("Architecture", font_size=44, color=BLUE_PRIMARY, weight=BOLD)
        header.move_to(UP * 7)
        self.play(FadeIn(header), run_time=0.4)

        # Layer 1: Client
        client_box = self._make_box("Client / SDK", SLATE, 3.5, 0.8)
        client_box.move_to(UP * 5)

        # Layer 2: API Services
        api_label = Text("API Layer", font_size=22, color=GRAY)
        api_label.move_to(UP * 3.8)

        services = VGroup()
        svc_names = ["Job\n:8001", "Meta\n:8002", "Log\n:8003", "Store\n:8004"]
        for name in svc_names:
            svc = self._make_box(name, BLUE_DARK, 1.8, 1.0)
            services.add(svc)
        services.arrange(RIGHT, buff=0.2)
        services.move_to(UP * 2.5)

        # Layer 3: Kafka
        kafka_box = self._make_box("Kafka  (Events)", INDIGO, 5.0, 0.8)
        kafka_box.move_to(UP * 0.5)

        # Layer 4: Orchestrator
        orch_box = self._make_box("Orchestrator", ORANGE, 4.0, 0.8)
        orch_box.move_to(DOWN * 1.2)

        # Layer 5: Spark on K8s
        spark_box = self._make_box("Spark on Kubernetes", GREEN, 5.5, 1.0)
        spark_box.move_to(DOWN * 3.0)

        # Layer 6: Data stores
        stores = VGroup()
        store_names = ["PostgreSQL", "MinIO/S3", "Loki"]
        for name in store_names:
            s = self._make_box(name, SLATE, 2.2, 0.7)
            stores.add(s)
        stores.arrange(RIGHT, buff=0.2)
        stores.move_to(DOWN * 5.2)

        # Arrows
        arrow1 = Arrow(client_box.get_bottom(), services.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow2 = Arrow(services[0].get_bottom(), kafka_box.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow3 = Arrow(kafka_box.get_bottom(), orch_box.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow4 = Arrow(orch_box.get_bottom(), spark_box.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow5 = Arrow(spark_box.get_bottom(), stores.get_top(), color=GRAY, buff=0.15, stroke_width=2)

        # Callback arrow (curved)
        callback = CurvedArrow(
            spark_box.get_right() + RIGHT * 0.1,
            services[0].get_right() + RIGHT * 0.1,
            color=GREEN, angle=-TAU / 4,
        )
        cb_label = Text("callback", font_size=16, color=GREEN)
        cb_label.next_to(callback, RIGHT, buff=0.1)

        # Animate layer by layer
        self.play(GrowFromCenter(client_box), run_time=0.5)
        self.play(Create(arrow1), run_time=0.3)
        self.play(FadeIn(api_label), run_time=0.2)
        self.play(
            LaggedStart(*[GrowFromCenter(s) for s in services], lag_ratio=0.1),
            run_time=1.0,
        )
        self.play(Create(arrow2), run_time=0.3)
        self.play(GrowFromCenter(kafka_box), run_time=0.5)
        self.play(Create(arrow3), run_time=0.3)
        self.play(GrowFromCenter(orch_box), run_time=0.5)
        self.play(Create(arrow4), run_time=0.3)
        self.play(GrowFromCenter(spark_box), run_time=0.6)
        self.play(Create(arrow5), run_time=0.3)
        self.play(
            LaggedStart(*[GrowFromCenter(s) for s in stores], lag_ratio=0.1),
            run_time=0.8,
        )
        self.wait(0.5)
        self.play(Create(callback), FadeIn(cb_label), run_time=0.8)
        self.wait(2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

    def _make_box(self, text, color, width, height):
        rect = RoundedRectangle(
            width=width, height=height, corner_radius=0.15,
            fill_color=color, fill_opacity=0.9,
            stroke_color=WHITE, stroke_width=1,
        )
        label = Text(text, font_size=20, color=WHITE)
        label.move_to(rect.get_center())
        return VGroup(rect, label)


class FeaturesScene(Scene):
    """Scene 4: Features showcase (20 seconds)"""

    def construct(self):
        header = Text("Key Features", font_size=44, color=BLUE_PRIMARY, weight=BOLD)
        header.move_to(UP * 7)
        self.play(FadeIn(header), run_time=0.4)

        features = [
            ("⚡", "REST API Job Submission", "Submit, cancel, track, retry"),
            ("🔄", "Auto-Retry on Failure", "Configurable max retries + dead-letter"),
            ("📊", "Metadata Catalog", "Schema evolution + Iceberg snapshots"),
            ("☁️", "S3 Object Storage", "MinIO locally, production S3 ready"),
            ("📈", "Full Observability", "Prometheus + Grafana + Loki"),
            ("🐳", "K8s Isolated Runtime", "One pod per job, NetworkPolicy"),
            ("🔒", "API Key Auth", "External + internal token model"),
            ("📋", "Event-Driven", "Kafka decouples submit from execute"),
        ]

        cards = VGroup()
        for emoji, title, desc in features:
            icon = Text(emoji, font_size=28)
            title_text = Text(title, font_size=24, color=WHITE, weight=BOLD)
            desc_text = Text(desc, font_size=18, color=GRAY)
            content = VGroup(title_text, desc_text).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            row = VGroup(icon, content).arrange(RIGHT, buff=0.4, aligned_edge=UP)
            cards.add(row)

        cards.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        cards.move_to(DOWN * 0.5)
        cards.scale_to_fit_width(7.5)

        for card in cards:
            self.play(FadeIn(card, shift=RIGHT * 0.5), run_time=0.35)

        self.wait(2.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)


class CTAScene(Scene):
    """Scene 5: Call to action (15 seconds)"""

    def construct(self):
        # Star animation
        star = Text("⭐", font_size=72)
        star.move_to(UP * 4)
        self.play(GrowFromCenter(star), run_time=0.5)
        self.play(star.animate.scale(1.3), run_time=0.3)
        self.play(star.animate.scale(1 / 1.3), run_time=0.3)

        # Open Source badge
        oss = Text("100% Open Source", font_size=40, color=GREEN, weight=BOLD)
        oss.move_to(UP * 2)
        self.play(FadeIn(oss, shift=UP * 0.3), run_time=0.5)

        # Repo URL
        url_text = Text(
            "github.com/Abhishek543-dotcom/\nOn-premise-Data-Highway-Platform-DHP",
            font_size=22, color=CYAN, line_spacing=1.3,
        )
        url_text.move_to(ORIGIN)
        self.play(FadeIn(url_text, shift=UP * 0.3), run_time=0.6)

        # Docs
        docs_text = Text(
            "Live Docs & Architecture",
            font_size=26, color=WHITE,
        )
        docs_text.move_to(DOWN * 2)
        self.play(FadeIn(docs_text), run_time=0.4)

        # CTA
        cta_box = RoundedRectangle(
            width=6, height=1.2, corner_radius=0.3,
            fill_color=BLUE_PRIMARY, fill_opacity=1,
            stroke_width=0,
        )
        cta_text = Text("Star ⭐ & Contribute", font_size=32, color=WHITE, weight=BOLD)
        cta_text.move_to(cta_box.get_center())
        cta = VGroup(cta_box, cta_text)
        cta.move_to(DOWN * 4.5)
        self.play(GrowFromCenter(cta), run_time=0.6)

        # Pulse the CTA
        self.play(
            cta.animate.scale(1.05), rate_func=there_and_back, run_time=0.6,
        )
        self.play(
            cta.animate.scale(1.05), rate_func=there_and_back, run_time=0.6,
        )

        # Author
        author = Text("Built by Abhishek Tiwari", font_size=22, color=GRAY)
        author.move_to(DOWN * 6.5)
        self.play(FadeIn(author), run_time=0.4)

        self.wait(2.0)


class FullVideo(Scene):
    """Complete video: all scenes in sequence."""

    def construct(self):
        # === SCENE 1: Title (5s) ===
        title = Text("DataHarbour", font_size=72, color=WHITE, weight=BOLD)
        title.move_to(UP * 2)
        subtitle = Text("Project (DHP)", font_size=42, color=BLUE_PRIMARY)
        subtitle.next_to(title, DOWN, buff=0.3)
        tagline = Text(
            "A Complete Data Lakehouse\nPlatform from Scratch",
            font_size=32, color=GRAY, line_spacing=1.2,
        )
        tagline.next_to(subtitle, DOWN, buff=1.0)

        techs = ["Python", "FastAPI", "Spark", "Kafka", "K8s"]
        badges = VGroup()
        for tech in techs:
            badge = VGroup(
                RoundedRectangle(
                    width=1.8, height=0.6, corner_radius=0.2,
                    fill_color=SLATE, fill_opacity=1, stroke_color=BLUE_PRIMARY, stroke_width=1
                ),
                Text(tech, font_size=20, color=CYAN),
            )
            badge[1].move_to(badge[0].get_center())
            badges.add(badge)
        badges.arrange_in_grid(rows=2, cols=3, buff=0.3)
        badges.next_to(tagline, DOWN, buff=1.2)

        self.play(Write(title), run_time=0.8)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.5)
        self.play(FadeIn(tagline, shift=UP * 0.3), run_time=0.7)
        self.play(
            LaggedStart(*[GrowFromCenter(b) for b in badges], lag_ratio=0.15),
            run_time=1.2,
        )
        self.wait(1.5)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        # === SCENE 2: Problem (10s) ===
        header = Text("The Problem", font_size=48, color=RED, weight=BOLD)
        header.move_to(UP * 6)
        self.play(FadeIn(header, shift=DOWN * 0.3), run_time=0.5)

        problems = [
            "Manual Spark job management",
            "No retry logic on failures",
            "Scattered logs everywhere",
            "Zero observability",
            "No metadata governance",
        ]
        pain_group = VGroup()
        for problem in problems:
            cross = Text("✗", font_size=36, color=RED)
            text = Text(problem, font_size=28, color=WHITE)
            row = VGroup(cross, text).arrange(RIGHT, buff=0.3)
            pain_group.add(row)
        pain_group.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        pain_group.move_to(UP * 1.5)

        for row in pain_group:
            self.play(FadeIn(row, shift=LEFT * 0.5), run_time=0.4)
        self.wait(0.8)

        solution_text = Text("There's a better way →", font_size=36, color=GREEN, weight=BOLD)
        solution_text.move_to(DOWN * 4)
        self.play(FadeIn(solution_text, shift=UP * 0.5), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.4)

        # === SCENE 3: Architecture (25s) ===
        header = Text("Architecture", font_size=44, color=BLUE_PRIMARY, weight=BOLD)
        header.move_to(UP * 7)
        self.play(FadeIn(header), run_time=0.4)

        def make_box(text, color, width, height):
            rect = RoundedRectangle(
                width=width, height=height, corner_radius=0.15,
                fill_color=color, fill_opacity=0.9,
                stroke_color=WHITE, stroke_width=1,
            )
            label = Text(text, font_size=20, color=WHITE)
            label.move_to(rect.get_center())
            return VGroup(rect, label)

        client_box = make_box("Client / SDK", SLATE, 3.5, 0.8)
        client_box.move_to(UP * 5)

        api_label = Text("API Layer", font_size=22, color=GRAY)
        api_label.move_to(UP * 3.8)

        services = VGroup()
        for name in ["Job\n:8001", "Meta\n:8002", "Log\n:8003", "Store\n:8004"]:
            services.add(make_box(name, BLUE_DARK, 1.8, 1.0))
        services.arrange(RIGHT, buff=0.2)
        services.move_to(UP * 2.5)

        kafka_box = make_box("Kafka  (Events)", INDIGO, 5.0, 0.8)
        kafka_box.move_to(UP * 0.5)

        orch_box = make_box("Orchestrator", ORANGE, 4.0, 0.8)
        orch_box.move_to(DOWN * 1.2)

        spark_box = make_box("Spark on Kubernetes", GREEN, 5.5, 1.0)
        spark_box.move_to(DOWN * 3.0)

        stores = VGroup()
        for name in ["PostgreSQL", "MinIO/S3", "Loki"]:
            stores.add(make_box(name, SLATE, 2.2, 0.7))
        stores.arrange(RIGHT, buff=0.2)
        stores.move_to(DOWN * 5.2)

        arrow1 = Arrow(client_box.get_bottom(), services.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow2 = Arrow(services[0].get_bottom(), kafka_box.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow3 = Arrow(kafka_box.get_bottom(), orch_box.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow4 = Arrow(orch_box.get_bottom(), spark_box.get_top(), color=GRAY, buff=0.15, stroke_width=2)
        arrow5 = Arrow(spark_box.get_bottom(), stores.get_top(), color=GRAY, buff=0.15, stroke_width=2)

        callback = CurvedArrow(
            spark_box.get_right() + RIGHT * 0.1,
            services[0].get_right() + RIGHT * 0.1,
            color=GREEN, angle=-TAU / 4,
        )
        cb_label = Text("callback", font_size=16, color=GREEN)
        cb_label.next_to(callback, RIGHT, buff=0.1)

        self.play(GrowFromCenter(client_box), run_time=0.5)
        self.play(Create(arrow1), run_time=0.3)
        self.play(FadeIn(api_label), run_time=0.2)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in services], lag_ratio=0.1), run_time=1.0)
        self.play(Create(arrow2), run_time=0.3)
        self.play(GrowFromCenter(kafka_box), run_time=0.5)
        self.play(Create(arrow3), run_time=0.3)
        self.play(GrowFromCenter(orch_box), run_time=0.5)
        self.play(Create(arrow4), run_time=0.3)
        self.play(GrowFromCenter(spark_box), run_time=0.6)
        self.play(Create(arrow5), run_time=0.3)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in stores], lag_ratio=0.1), run_time=0.8)
        self.wait(0.5)
        self.play(Create(callback), FadeIn(cb_label), run_time=0.8)
        self.wait(2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        # === SCENE 4: Features (20s) ===
        header = Text("Key Features", font_size=44, color=BLUE_PRIMARY, weight=BOLD)
        header.move_to(UP * 7)
        self.play(FadeIn(header), run_time=0.4)

        features = [
            ("⚡", "REST API Job Submission", "Submit, cancel, track, retry"),
            ("🔄", "Auto-Retry on Failure", "Configurable max retries"),
            ("📊", "Metadata Catalog", "Schema evolution + snapshots"),
            ("☁️", "S3 Object Storage", "MinIO local, production ready"),
            ("📈", "Full Observability", "Prometheus + Grafana + Loki"),
            ("🐳", "K8s Isolated Runtime", "One pod per Spark job"),
            ("🔒", "API Key Auth", "External + internal tokens"),
            ("📋", "Event-Driven", "Kafka async orchestration"),
        ]

        cards = VGroup()
        for emoji, feat_title, desc in features:
            icon = Text(emoji, font_size=28)
            title_text = Text(feat_title, font_size=24, color=WHITE, weight=BOLD)
            desc_text = Text(desc, font_size=18, color=GRAY)
            content = VGroup(title_text, desc_text).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            row = VGroup(icon, content).arrange(RIGHT, buff=0.4, aligned_edge=UP)
            cards.add(row)
        cards.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        cards.move_to(DOWN * 0.5)
        cards.scale_to_fit_width(7.5)

        for card in cards:
            self.play(FadeIn(card, shift=RIGHT * 0.5), run_time=0.35)
        self.wait(2.0)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)

        # === SCENE 5: CTA (15s) ===
        star = Text("⭐", font_size=72)
        star.move_to(UP * 4)
        self.play(GrowFromCenter(star), run_time=0.5)
        self.play(star.animate.scale(1.3), run_time=0.3)
        self.play(star.animate.scale(1 / 1.3), run_time=0.3)

        oss = Text("100% Open Source", font_size=40, color=GREEN, weight=BOLD)
        oss.move_to(UP * 2)
        self.play(FadeIn(oss, shift=UP * 0.3), run_time=0.5)

        url_text = Text(
            "github.com/Abhishek543-dotcom/\nOn-premise-Data-Highway-Platform-DHP",
            font_size=22, color=CYAN, line_spacing=1.3,
        )
        url_text.move_to(ORIGIN)
        self.play(FadeIn(url_text, shift=UP * 0.3), run_time=0.6)

        docs_text = Text("Live Docs & Architecture", font_size=26, color=WHITE)
        docs_text.move_to(DOWN * 2)
        self.play(FadeIn(docs_text), run_time=0.4)

        cta_box = RoundedRectangle(
            width=6, height=1.2, corner_radius=0.3,
            fill_color=BLUE_PRIMARY, fill_opacity=1, stroke_width=0,
        )
        cta_text = Text("Star ⭐ & Contribute", font_size=32, color=WHITE, weight=BOLD)
        cta_text.move_to(cta_box.get_center())
        cta = VGroup(cta_box, cta_text)
        cta.move_to(DOWN * 4.5)
        self.play(GrowFromCenter(cta), run_time=0.6)
        self.play(cta.animate.scale(1.05), rate_func=there_and_back, run_time=0.6)
        self.play(cta.animate.scale(1.05), rate_func=there_and_back, run_time=0.6)

        author = Text("Built by Abhishek Tiwari", font_size=22, color=GRAY)
        author.move_to(DOWN * 6.5)
        self.play(FadeIn(author), run_time=0.4)
        self.wait(2.0)
