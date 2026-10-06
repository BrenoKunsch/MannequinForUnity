bl_info = {
    "name": "Mannequin Medium Humanoid IK",
    "author": "OpenAI",
    "version": (1, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Humanoid IK",
    "description": "Create the Mannequin Medium skeleton or import its FBX, with optional IK",
    "category": "Rigging",
}

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Operator, Panel
from mathutils import Vector

# Exact deform-bone names and parent relationships from Mannequin_Medium.fbx.
PARENTS = {
    "root": None, "hips": "root", "spine": "hips", "chest": "spine",
    "head": "chest",
    "upperarm.l": "chest", "lowerarm.l": "upperarm.l", "wrist.l": "lowerarm.l",
    "hand.l": "wrist.l", "handslot.l": "hand.l",
    "upperarm.r": "chest", "lowerarm.r": "upperarm.r", "wrist.r": "lowerarm.r",
    "hand.r": "wrist.r", "handslot.r": "hand.r",
    "upperleg.l": "hips", "lowerleg.l": "upperleg.l", "foot.l": "lowerleg.l",
    "toes.l": "foot.l", "upperleg.r": "hips", "lowerleg.r": "upperleg.r",
    "foot.r": "lowerleg.r", "toes.r": "foot.r",
}


def create_skeleton(context, height):
    """Build the exact source hierarchy with a T-pose proportion template.

    Coordinates are a modeling starting point, not measurements of the FBX.
    """
    scale = height / 1.8
    layout = {
        'root': ((0, 0, 0), (0, 0, 0.12)),
        'hips': ((0, 0, 0.96), (0, 0, 1.08)),
        'spine': ((0, 0, 1.08), (0, 0, 1.31)),
        'chest': ((0, 0, 1.31), (0, 0, 1.53)),
        'head': ((0, 0, 1.53), (0, 0, 1.79)),
    }
    for side, sign in (('l', 1), ('r', -1)):
        def v(x, y, z):
            return (sign * x, y, z)
        layout.update({
            'upperarm.' + side: (v(0.18, 0, 1.48), v(0.48, 0, 1.44)),
            'lowerarm.' + side: (v(0.48, 0, 1.44), v(0.75, 0, 1.40)),
            'wrist.' + side: (v(0.75, 0, 1.40), v(0.79, 0, 1.40)),
            'hand.' + side: (v(0.79, 0, 1.40), v(0.89, 0, 1.40)),
            'handslot.' + side: (v(0.89, 0, 1.40), v(0.94, 0, 1.40)),
            'upperleg.' + side: (v(0.10, 0, 0.96), v(0.12, -0.025, 0.55)),
            'lowerleg.' + side: (v(0.12, -0.025, 0.55), v(0.12, 0, 0.12)),
            'foot.' + side: (v(0.12, 0, 0.12), v(0.12, -0.15, 0.06)),
            'toes.' + side: (v(0.12, -0.15, 0.06), v(0.12, -0.24, 0.06)),
        })
    if context.object and context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    data = bpy.data.armatures.new('Rig_Medium')
    armature = bpy.data.objects.new('Rig_Medium', data)
    context.collection.objects.link(armature)
    for obj in context.selected_objects:
        obj.select_set(False)
    armature.select_set(True)
    context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='EDIT')
    for name, parent_name in PARENTS.items():
        head, tail = layout[name]
        bone = data.edit_bones.new(name)
        bone.head = Vector(head) * scale
        bone.tail = Vector(tail) * scale
        if parent_name:
            bone.parent = data.edit_bones[parent_name]
        bone.use_connect = False
    bpy.ops.object.mode_set(mode='OBJECT')
    armature.show_in_front = True
    data.display_type = 'STICK'
    check_skeleton(armature)
    return armature


def check_skeleton(armature):
    missing = [name for name in PARENTS if name not in armature.data.bones]
    if missing:
        raise ValueError("Ossos ausentes: " + ", ".join(missing))
    wrong = []
    for name, parent in PARENTS.items():
        bone = armature.data.bones[name]
        actual = bone.parent.name if bone.parent else None
        if actual != parent:
            wrong.append("%s (pai: %s; esperado: %s)" % (name, actual, parent))
    if wrong:
        raise ValueError("Hierarquia diferente do FBX: " + "; ".join(wrong))


def remove_control(armature, name):
    bone = armature.data.edit_bones.get(name)
    if bone:
        armature.data.edit_bones.remove(bone)


def create_control(armature, name, position, size, parent, direction):
    bone = armature.data.edit_bones.new(name)
    bone.head = position
    bone.tail = position + direction.normalized() * max(size, 0.025)
    bone.parent = parent
    bone.use_connect = False
    bone.use_deform = False
    return bone


def build_controls(armature, pole_distance):
    check_skeleton(armature)
    view_layer = bpy.context.view_layer
    previous_active = view_layer.objects.active
    previous_mode = bpy.context.object.mode if bpy.context.object else 'OBJECT'
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    view_layer.objects.active = armature
    armature.select_set(True)
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        eb = armature.data.edit_bones
        root = eb['root']
        for side in ('l', 'r'):
            for limb in ('arm', 'leg'):
                upper_name = ('upperarm.' if limb == 'arm' else 'upperleg.') + side
                lower_name = ('lowerarm.' if limb == 'arm' else 'lowerleg.') + side
                end_name = ('wrist.' if limb == 'arm' else 'foot.') + side
                upper, lower, end = eb[upper_name], eb[lower_name], eb[end_name]
                start = upper.head.copy()
                joint = lower.head.copy()
                goal = end.head.copy()
                line = goal - start
                if line.length < 0.0001:
                    raise ValueError("Cadeia de comprimento zero: " + lower_name)
                line_dir = line.normalized()
                bend = joint - (start + line_dir * (joint - start).dot(line_dir))
                if bend.length < 0.0001:
                    # Straight T-pose: derive a stable pole from local bone orientation.
                    bend = upper.x_axis - line_dir * upper.x_axis.dot(line_dir)
                if bend.length < 0.0001:
                    bend = line_dir.cross(Vector((0, 0, 1)))
                if bend.length < 0.0001:
                    bend = line_dir.cross(Vector((0, 1, 0)))
                reach = (joint - start).length + (goal - joint).length
                pole_pos = joint + bend.normalized() * max(reach * pole_distance, 0.1)
                size = max(reach * 0.14, 0.05)
                target_name = 'IK_' + limb + '_target.' + side
                pole_name = 'IK_' + limb + '_pole.' + side
                remove_control(armature, target_name)
                remove_control(armature, pole_name)
                direction = Vector((0, 0, 1)) if limb == 'leg' else Vector((0, 1, 0))
                create_control(armature, target_name, goal, size, root, direction)
                create_control(armature, pole_name, pole_pos, size * 0.8, root, direction)
        bpy.ops.object.mode_set(mode='OBJECT')
        for side in ('l', 'r'):
            for limb in ('arm', 'leg'):
                lower_name = ('lowerarm.' if limb == 'arm' else 'lowerleg.') + side
                end_name = ('wrist.' if limb == 'arm' else 'foot.') + side
                target_name = 'IK_' + limb + '_target.' + side
                pole_name = 'IK_' + limb + '_pole.' + side
                lower = armature.pose.bones[lower_name]
                for constraint in tuple(lower.constraints):
                    if constraint.name == 'Mannequin IK':
                        lower.constraints.remove(constraint)
                ik = lower.constraints.new('IK')
                ik.name = 'Mannequin IK'
                ik.target = armature
                ik.subtarget = target_name
                ik.pole_target = armature
                ik.pole_subtarget = pole_name
                ik.chain_count = 2
                ik.use_stretch = False
                ik.pole_angle = armature.mannequin_pole_angle
                # The FK wrist/foot stays in the original hierarchy. Match its
                # orientation to the IK control without changing bone parenting.
                end = armature.pose.bones[end_name]
                for constraint in tuple(end.constraints):
                    if constraint.name == 'Mannequin IK orientation':
                        end.constraints.remove(constraint)
                rotation = end.constraints.new('COPY_ROTATION')
                rotation.name = 'Mannequin IK orientation'
                rotation.target = armature
                rotation.subtarget = target_name
                rotation.target_space = 'WORLD'
                rotation.owner_space = 'WORLD'
                rotation.influence = 0.0  # Enable manually if wrist/foot rotation is wanted.
                for name in (target_name, pole_name):
                    armature.data.bones[name].hide = False
        armature['mannequin_ik_installed'] = True
        armature.show_in_front = True
        armature.data.display_type = 'STICK'
    finally:
        if armature.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        if previous_active and previous_active.name in bpy.data.objects:
            view_layer.objects.active = previous_active
            if previous_active == armature and previous_mode in {'POSE', 'EDIT'}:
                bpy.ops.object.mode_set(mode=previous_mode)


class MANNEQUIN_OT_import_and_build(Operator):
    bl_idname = 'mannequin.import_and_build'
    bl_label = 'Importar ossos do FBX'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.mannequin_ik_settings
        if not settings.fbx_path:
            self.report({'ERROR'}, 'Selecione o arquivo Mannequin_Medium.fbx')
            return {'CANCELLED'}
        path = bpy.path.abspath(settings.fbx_path)
        try:
            before = set(bpy.data.objects)
            bpy.ops.import_scene.fbx(filepath=path)
            new_armatures = [obj for obj in set(bpy.data.objects) - before if obj.type == 'ARMATURE']
            matching = [obj for obj in new_armatures if all(n in obj.data.bones for n in PARENTS)]
            if len(matching) != 1:
                raise ValueError('O FBX deve conter exatamente um armature com os ossos esperados')
            armature = matching[0]
            check_skeleton(armature)
            if settings.create_ik:
                build_controls(armature, settings.pole_distance)
            context.view_layer.objects.active = armature
            armature.select_set(True)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Rig importado' + (' com IK' if settings.create_ik else ' sem IK'))
        return {'FINISHED'}


class MANNEQUIN_OT_create_skeleton(Operator):
    bl_idname = 'mannequin.create_skeleton'
    bl_label = 'Criar ossos do zero'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.mannequin_ik_settings
        try:
            armature = create_skeleton(context, settings.height)
            if settings.create_ik:
                build_controls(armature, settings.pole_distance)
                context.view_layer.objects.active = armature
                armature.select_set(True)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Ossos criados' + (' com IK' if settings.create_ik else ' sem IK'))
        return {'FINISHED'}


class MANNEQUIN_OT_add_ik(Operator):
    bl_idname = 'mannequin.add_ik'
    bl_label = 'Adicionar IK ao armature selecionado'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        try:
            build_controls(context.active_object, context.scene.mannequin_ik_settings.pole_distance)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, 'Quatro cadeias IK configuradas')
        return {'FINISHED'}


class MANNEQUIN_OT_update_poles(Operator):
    bl_idname = 'mannequin.update_poles'
    bl_label = 'Aplicar ângulo dos pole targets'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        armature = context.active_object
        for side in ('l', 'r'):
            for limb in ('arm', 'leg'):
                name = ('lowerarm.' if limb == 'arm' else 'lowerleg.') + side
                bone = armature.pose.bones.get(name)
                if bone:
                    for constraint in bone.constraints:
                        if constraint.name == 'Mannequin IK' and constraint.type == 'IK':
                            constraint.pole_angle = armature.mannequin_pole_angle
        return {'FINISHED'}


class MANNEQUIN_PG_settings(bpy.types.PropertyGroup):
    fbx_path: StringProperty(name='Mannequin FBX', subtype='FILE_PATH')
    height: FloatProperty(name='Altura (m)', default=1.8, min=0.2, max=10.0)
    create_ik: BoolProperty(name='Criar controles IK', default=False)
    pole_distance: FloatProperty(name='Distância dos poles', default=0.65, min=0.15, max=3.0)


class MANNEQUIN_PT_panel(Panel):
    bl_label = 'Mannequin Humanoid IK'
    bl_idname = 'MANNEQUIN_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Humanoid IK'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.mannequin_ik_settings
        layout.prop(settings, 'height')
        layout.prop(settings, 'create_ik')
        layout.operator('mannequin.create_skeleton', icon='ARMATURE_DATA')
        layout.separator()
        layout.prop(settings, 'fbx_path')
        layout.operator('mannequin.import_and_build', icon='IMPORT')
        layout.separator()
        if settings.create_ik:
            layout.prop(settings, 'pole_distance')
        layout.operator('mannequin.add_ik', icon='CONSTRAINT_BONE')
        if context.active_object and context.active_object.type == 'ARMATURE':
            layout.prop(context.active_object, 'mannequin_pole_angle', text='Ângulo IK')
            layout.operator('mannequin.update_poles')
        layout.label(text='Controles IK: Pose Mode')
        layout.label(text='Unity: exportar apenas deform bones')


CLASSES = (MANNEQUIN_PG_settings, MANNEQUIN_OT_import_and_build,
           MANNEQUIN_OT_create_skeleton,
           MANNEQUIN_OT_add_ik, MANNEQUIN_OT_update_poles, MANNEQUIN_PT_panel)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.mannequin_ik_settings = bpy.props.PointerProperty(type=MANNEQUIN_PG_settings)
    bpy.types.Object.mannequin_pole_angle = FloatProperty(
        name='Ângulo dos poles', subtype='ANGLE', default=0.0,
        description='Ajuste se o cotovelo/joelho girar ao ativar o IK')


def unregister():
    del bpy.types.Object.mannequin_pole_angle
    del bpy.types.Scene.mannequin_ik_settings
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
