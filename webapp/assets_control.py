from flask.ext.assets import Bundle as AssetsBundle
from flask.ext.assets import Environment as AssetsEnvironment
import glob


def register_static_resources(app):
    """
        Uses app as context to register static assets
        add new directory by creating glob and then Bundle

        (current bundles)
            - css
            - js
    """
    assets = AssetsEnvironment(app)
    cutoff = len('webapp/static/')
    js_files = glob.glob("webapp/static/js/*.js")
    js_bundle = [fname[cutoff:] for fname in js_files]

    js_bundle = AssetsBundle(
        # framework stuff
        AssetsBundle(
            *js_bundle
        ),
        output='gen/packed.js'
    )

    css_files = glob.glob("webapp/static/css/*.css")
    css_bundle = [fname[cutoff:] for fname in css_files]
    css_bundle = AssetsBundle(
        AssetsBundle(
            *css_bundle
        ),
        output='gen/packed.css'
    )
    assets.register('js_all', js_bundle)
    assets.register('css_all', css_bundle)

    # style_files = glob.glob("static/css/*.css")
    # style_bundle = [fname[cutoff:] for fname in style_files]
