from __future__ import annotations

import json
import struct
import zipfile
from io import BytesIO

from myth_forge_api.domain.models import (
    GeneratedAssetVariant,
    MythSession,
    PrintCandidate,
)


def local_generated_game_glb(session_id: str) -> bytes:
    payload = {
        "asset": {
            "version": "2.0",
            "generator": "Personal Myth Forge local provider",
        },
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": f"{session_id}-local-game-asset"}],
    }
    json_chunk = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    json_chunk += b" " * ((4 - len(json_chunk) % 4) % 4)
    total_length = 12 + 8 + len(json_chunk)
    return (
        b"glTF"
        + struct.pack("<II", 2, total_length)
        + struct.pack("<I4s", len(json_chunk), b"JSON")
        + json_chunk
    )


def local_generated_scene_dae(session_id: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
  <asset>
    <contributor>
      <authoring_tool>Personal Myth Forge local provider</authoring_tool>
    </contributor>
    <unit name="meter" meter="1"/>
    <up_axis>Y_UP</up_axis>
  </asset>
  <library_effects>
    <effect id="relic-effect">
      <profile_COMMON>
        <technique sid="common">
          <phong>
            <diffuse>
              <color>0.04 0.72 0.68 1</color>
            </diffuse>
            <specular>
              <color>0.8 0.9 0.88 1</color>
            </specular>
            <shininess>
              <float>42</float>
            </shininess>
          </phong>
        </technique>
      </profile_COMMON>
    </effect>
  </library_effects>
  <library_materials>
    <material id="relic-material" name="Local Generated Relic">
      <instance_effect url="#relic-effect"/>
    </material>
  </library_materials>
  <library_geometries>
    <geometry id="{session_id}-geometry" name="{session_id}-local-relic">
      <mesh>
        <source id="{session_id}-positions">
          <float_array id="{session_id}-positions-array" count="12">
            0 0.72 0 -0.62 -0.42 0.44 0.62 -0.42 0.44 0 -0.42 -0.62
          </float_array>
          <technique_common>
            <accessor source="#{session_id}-positions-array" count="4" stride="3">
              <param name="X" type="float"/>
              <param name="Y" type="float"/>
              <param name="Z" type="float"/>
            </accessor>
          </technique_common>
        </source>
        <vertices id="{session_id}-vertices">
          <input semantic="POSITION" source="#{session_id}-positions"/>
        </vertices>
        <triangles material="relic-material" count="4">
          <input semantic="VERTEX" source="#{session_id}-vertices" offset="0"/>
          <p>0 1 2 0 2 3 0 3 1 1 3 2</p>
        </triangles>
      </mesh>
    </geometry>
  </library_geometries>
  <library_visual_scenes>
    <visual_scene id="scene" name="Personal Myth Forge Local Scene">
      <node id="{session_id}-node" name="Generated Relic">
        <instance_geometry url="#{session_id}-geometry">
          <bind_material>
            <technique_common>
              <instance_material symbol="relic-material" target="#relic-material"/>
            </technique_common>
          </bind_material>
        </instance_geometry>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene>
    <instance_visual_scene url="#scene"/>
  </scene>
</COLLADA>
"""


def local_generated_print_3mf(session_id: str) -> bytes:
    model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
          <vertex x="0" y="8" z="0"/>
          <vertex x="-6" y="-4" z="4"/>
          <vertex x="6" y="-4" z="4"/>
          <vertex x="0" y="-4" z="-6"/>
        </vertices>
        <triangles>
          <triangle v1="0" v2="1" v3="2"/>
          <triangle v1="0" v2="2" v3="3"/>
          <triangle v1="0" v2="3" v3="1"/>
          <triangle v1="1" v2="3" v3="2"/>
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
  </build>
  <metadata name="Title">Personal Myth Forge {session_id} print candidate</metadata>
</model>
"""
    rels_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""
    content_types_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types_xml)
        archive.writestr("_rels/.rels", rels_xml)
        archive.writestr("3D/3dmodel.model", model_xml)
    return buffer.getvalue()


def with_served_local_generated_asset_urls(
    session: MythSession,
    *,
    base_url: str,
) -> MythSession:
    if session.generated_asset.provider != "local_stub":
        return session

    asset = session.generated_asset
    game_url = _asset_url(base_url, session.session_id, "game.glb")
    scene_url = _asset_url(base_url, session.session_id, "scene.dae")
    print_url = _print_candidate_url(base_url, session.session_id)
    variants = [_served_variant(variant, game_url=game_url, scene_url=scene_url) for variant in asset.variants]
    served_asset = asset.model_copy(
        update={
            "uri": game_url if _is_local_generated_asset_uri(asset.uri) else asset.uri,
            "variants": variants,
        }
    )
    return session.model_copy(
        update={
            "generated_asset": served_asset,
            "print_candidate": _served_print_candidate(
                session.print_candidate,
                old_source_uri=asset.uri,
                game_url=game_url,
                print_url=print_url,
            ),
        }
    )


def _served_variant(
    variant: GeneratedAssetVariant,
    *,
    game_url: str,
    scene_url: str,
) -> GeneratedAssetVariant:
    if not _is_local_generated_asset_uri(variant.uri):
        return variant
    if variant.role == "ios_scene_asset":
        return variant.model_copy(update={"uri": scene_url, "format": "dae"})
    if variant.role == "game_asset":
        return variant.model_copy(update={"uri": game_url})
    return variant


def _served_print_candidate(
    print_candidate: PrintCandidate,
    *,
    old_source_uri: str,
    game_url: str,
    print_url: str,
) -> PrintCandidate:
    if print_candidate.source_asset_uri != old_source_uri:
        return print_candidate
    return print_candidate.model_copy(
        update={
            "source_asset_uri": game_url,
            "uri": print_url
            if _is_local_print_candidate_uri(print_candidate.uri)
            else print_candidate.uri,
        }
    )


def _asset_url(base_url: str, session_id: str, filename: str) -> str:
    return f"{base_url.rstrip('/')}/v1/generated-assets/{session_id}/{filename}"


def _print_candidate_url(base_url: str, session_id: str) -> str:
    return f"{base_url.rstrip('/')}/v1/print-candidates/{session_id}/print.3mf"


def _is_local_generated_asset_uri(uri: str) -> bool:
    return uri.startswith("local://generated-assets/")


def _is_local_print_candidate_uri(uri: str) -> bool:
    return uri.startswith("local://print-candidates/")
