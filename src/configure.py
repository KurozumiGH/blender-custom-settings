import bpy


class BlenderCustomSettings:
    """
    Blenderのカスタム設定を行うクラス

    Blender 2.83.x シリーズを前提とした設定スクリプトになっているため、
    後続バージョンで互換性が無くなった対象についてはif文によるバージョンの分岐を入れる。
    サポートしているバージョンは`self.supports`に追加していく。
    """

    def __init__(self):
        self.ver = float(bpy.app.version_string[:4])  # ex: 2.83
        self.supports = [2.83]  # サポートバージョン

    # ================================================================
    # Utilities
    # ================================================================
    def check_version(self):
        """
        対応しているバージョンかどうかを確認する
        """
        return self.ver in self.supports

    def get_spaces(self, type_name, display_mode=None, screen_names=None):
        """
        指定された対象のspaceをlistで返す
        """
        target_spaces = []

        # 対象のscreenを絞り込み
        screens = bpy.data.screens
        if screen_names:
            screens = filter(lambda sc: sc.name in screen_names, screens)
        # screens.areas.spaces の絞り込み
        for screen in screens:
            for area in filter(lambda area: area.type == type_name, screen.areas):
                spaces = filter(lambda sp: sp.type == type_name, area.spaces)
                # display_modeによる絞り込み（指定されている場合）
                if display_mode:
                    spaces = filter(lambda sp: sp.display_mode == display_mode, spaces)
                # 最終的に残ったspaceを対象に追加
                for space in spaces:
                    target_spaces.append(space)

        return target_spaces

    # ================================================================
    # Scene settings
    # ================================================================
    def setup_scene_cycles(self):
        """
        Cyclesに関するシーン設定
        """
        scene = bpy.context.scene

        # Scene
        scene.render.engine = "CYCLES"  # Set render engine
        scene.cycles.feature_set = "EXPERIMENTAL"  # or "SUPPORTED"
        scene.cycles.device = "GPU"

        scene.cycles.preview_dicing_rate = 1  # Micropolygon pixel size

        # Denoising
        view_layer = bpy.context.view_layer
        view_layer.cycles.use_denoising = True
        view_layer.cycles.use_optix_denoising = True  # Use OptiX
        view_layer.cycles.denoising_optix_input_passes = "RGB_ALBEDO"  # Color+Albedo

        scene.cycles.preview_denoising = "NONE"  # or "OPTIX"

        # Sampling
        scene.cycles.samples = 128
        scene.cycles.preview_samples = 32
        scene.cycles.use_adaptive_sampling = True

        # Light Paths
        bounces = 32
        scene.cycles.max_bounces = bounces
        scene.cycles.diffuse_bounces = bounces
        scene.cycles.glossy_bounces = bounces
        scene.cycles.transparent_max_bounces = bounces
        scene.cycles.transmission_bounces = bounces
        scene.cycles.volume_bounces = bounces
        scene.cycles.caustics_reflective = True
        scene.cycles.caustics_refractive = True

        # Performance
        scene.render.threads_mode = "AUTO"
        scene.render.tile_x = 256
        scene.render.tile_y = 256
        scene.cycles.use_progressive_refine = False

    def setup_scene_shading(self):
        """
        Shading設定を行う
        """
        # 設定対象の画面（ShadingやTexture Paintなどは設定しない）
        target_screens = [
            "Layout",
            "Modeling",
            "Sculpting",
            "UV Editing",
            "Animation",
            "Scripting",
        ]
        for space in self.get_spaces("VIEW_3D", screen_names=target_screens):
            # RANDOMで色分け
            space.shading.type = "SOLID"
            space.shading.light = "STUDIO"
            space.shading.color_type = "RANDOM"
            # Cavity表示を有効化
            space.shading.show_cavity = True
            space.shading.cavity_type = "BOTH"
            space.shading.cavity_ridge_factor = 0.8
            space.shading.cavity_valley_factor = 1.0
            space.shading.curvature_ridge_factor = 0.8
            space.shading.curvature_valley_factor = 1.0

    def setup_scene_outliner(self):
        """
        Outliner（TreeView）の表示設定
        """
        # ViewLayerモードの場合選択とレンダリング設定を表示する
        for space in self.get_spaces("OUTLINER", display_mode="VIEW_LAYER"):
            space.show_restrict_column_select = True
            space.show_restrict_column_render = True

    def setup_scene_clipping(self):
        """
        ViewportとCameraのクリップ設定（描画される距離の範囲）
        """
        # 距離の開始/終了距離（単位m）
        start, end = 0.001, 1000

        # ViewportのClip設定
        for space in self.get_spaces("VIEW_3D"):
            space.clip_start = start
            space.clip_end = end
        # CameraのClip設定
        for cam in bpy.data.cameras:
            cam.clip_start = start
            cam.clip_end = end

    def setup_scene_scripting(self):
        """
        Scripting関係の設定
        """
        for space in self.get_spaces("CONSOLE"):
            space.font_size = 16  # Consoleのフォントサイズ

    # ================================================================
    # Preferences settings.
    # ================================================================
    def setup_preferences(self):
        """
        Preferencesの設定
        """
        pref = bpy.context.preferences

        # Interface > Display
        pref.view.ui_scale = 1.05
        pref.view.ui_line_width = "AUTO"
        pref.view.show_splash = False
        pref.view.show_tooltips = True
        pref.view.show_tooltips_python = True
        pref.view.show_developer_ui = False

        # Interface > Translation
        pref.view.language = "ja_JP"
        pref.view.use_translate_tooltips = True
        pref.view.use_translate_interface = False
        pref.view.use_translate_new_dataname = False

        # Themes > 3D Viewport > Face selected
        pref.themes[0].view_3d.face_select[3] = 0.4  # change alpha only

        # Viewport > Display
        pref.view.gizmo_size = 120

        # Input > Keyboard
        pref.inputs.use_numeric_input_advanced = True

        # Input > Mouse
        pref.inputs.mouse_double_click_time = 250
        pref.inputs.drag_threshold_mouse = 5
        pref.inputs.drag_threshold = 45
        pref.inputs.move_threshold = 3

        # Input > NDOF
        pref.inputs.ndof_show_guide = True
        pref.inputs.ndof_pan_yz_swap_axis = True

        # Navigation = Zoom
        pref.inputs.use_zoom_to_mouse = True

        # Keymap > Preferences
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.default  # keyconfigs["blender"]
        kc.preferences.spacebar_action = "SEARCH"

        # System > Cycles Render Devices
        pref.addons["cycles"].preferences.compute_device_type = "OPTIX"


# ================================================================
# Entry point
# ================================================================
if __name__ == "__main__":
    bcs = BlenderCustomSettings()

    if bcs.check_version():
        print("BlenderCustomSettings: Apply custom settings...")
        # Scene
        bcs.setup_scene_cycles()
        bcs.setup_scene_shading()
        bcs.setup_scene_outliner()
        bcs.setup_scene_clipping()
        bcs.setup_scene_scripting()
        # Preferences
        bcs.setup_preferences()

    else:
        print("BlenderCustomSettings: Unsupported version!")

    # clean
    del bcs
