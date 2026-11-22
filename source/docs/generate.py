"""Diagrama de pacotes a partir de AST de imports e diagrama de classes em Graphviz.

Execução: python source/docs/generate.py
Opcional: instalar 'graphviz' (dot) e 'pylint' (pyreverse) para integração UML.
"""
from __future__ import annotations
import ast
from pathlib import Path
import subprocess
import shutil
import re

ROOT = Path(__file__).resolve().parents[2]
MODULES = ROOT/'source'/'modules'
DOCS = ROOT/'docs'
PACKAGE_NAMES = {'engine','display','game','input','physics','entities','audio','ui','effects','config','constants'}


def find_deps(filename:Path):
    """Obtém dependências diretas de um módulo da pasta source/modules."""
    node=ast.parse(filename.read_text(encoding='utf-8'))
    parts=filename.relative_to(MODULES).with_suffix('').parts
    if parts[-1]=='__init__': parts=parts[:-1]
    current=list(parts[:-1])
    out=set()
    for entry in ast.walk(node):
        if isinstance(entry,ast.ImportFrom):
            if not entry.level:continue
            prefix = current[:max(0,len(current)-(entry.level-1))]
            if entry.module:prefix+=entry.module.split('.')
            if prefix and prefix[0] in PACKAGE_NAMES:out.add(prefix[0])
        elif isinstance(entry,ast.Import):
            for alias in entry.names:
                if alias.name.startswith('source.modules.'):
                    out.add(alias.name.split('.')[2])
    return out


def packages():
    mapping={}
    for path in MODULES.rglob('*.py'):
        if path.name=='__init__.py':continue
        rel=path.relative_to(MODULES)
        depname=rel.stem if len(rel.parts)==1 else rel.parts[0]
        if depname not in PACKAGE_NAMES:continue
        mapping.setdefault(depname,set()).update(find_deps(path))
    return {k:sorted(x for x in v if x!=k) for k,v in mapping.items()}


def write_package_diagram():
    mapping=packages()
    text=['digraph packages_game {','  graph [bgcolor="white",rankdir=LR,ranksep=1.0,nodesep=0.45];',
          '  node [shape=folder,style="rounded,filled",fillcolor="#EAF3FA",color="#30678D",fontname=Arial,fontsize=13];',
          '  edge [color="#7087A7",arrowsize=0.7];']
    for p in sorted(PACKAGE_NAMES):text.append(f'  "{p}";')
    for src,deps in sorted(mapping.items()):
        for dst in deps:text.append(f'  "{src}" -> "{dst}";')
    text.append('}')
    return '\n'.join(text),mapping


def write_class_diagram():
    content=r'''digraph classes_game {
    graph [bgcolor="white",rankdir=TB,ranksep=0.75,nodesep=0.45,splines=polyline];
    node [shape=record,style="filled",fillcolor="#EAF3FA",color="#30678D",fontname=Arial,fontsize=12];
    edge [color="#66799A",arrowsize=0.65,fontsize=10,fontname=Arial];
    GameEngine [label="{GameEngine|display, input, game, audio|run()}"];
    Display [label="{Display|backend, surface|tick()\npresent()}"];
    Game [label="{Game|players, balls, state|start_game()\nupdate(dt)\ncollide_world()}"];
    InputManager [label="{InputManager|left,right,launch|handle(event,game)}"];
    AudioManager [label="{AudioManager|sounds,muted|sound(),music_start()}"];
    Stage [label="{Stage|base,images|draw_playfield(),draw_hud()}"];
    SpriteSheet [label="{SpriteSheet|sheet,sprites,cache|get(name)}"];
    PlayerScore [label="{PlayerScore|score, remaining|add_points(),multiplier()}"];
    Ball [label="{Ball|position, velocity, radius|launch(),update()}"];
    TrajectoryController [label="{TrajectoryController|collision_manager|step(ball,dt)}"];
    CollisionManager [label="{CollisionManager| |circle_circle(),circle_segment()}"];
    Actuator [label="{Actuator| |activate()}"];
    Flipper [label="{Flipper|pivot,angle|update(),moving_at()}"];
    Plunger [label="{Plunger|charge|update(),release()}"];
    Obstacle [label="{Obstacle|x,y,radius|on_collide()}"];
    Bumper [label="{Bumper|points|on_collide()}"];
    Target [label="{Target|points|on_collide()}"];
    Hole [label="{Hole|points|on_collide()}"];
    Flipper -> Actuator [arrowhead=empty,label="herança"];
    Plunger -> Actuator [arrowhead=empty];
    Bumper -> Obstacle [arrowhead=empty,label="herança"];
    Target -> Obstacle [arrowhead=empty];
    Hole -> Obstacle [arrowhead=empty];
    GameEngine -> Display [arrowtail=diamond,dir=both];
    GameEngine -> Game [arrowtail=diamond,dir=both];
    GameEngine -> InputManager [arrowtail=diamond,dir=both];
    GameEngine -> AudioManager [arrowtail=diamond,dir=both];
    Game -> Stage [label="usa"];
    Stage -> SpriteSheet [arrowtail=diamond,dir=both,label="recortes do atlas"];
    Game -> Ball [arrowtail=diamond,dir=both,label="* bolas"];
    Game -> PlayerScore [arrowtail=diamond,dir=both,label="1..2 jogadores"];
    Game -> Flipper [arrowtail=diamond,dir=both,label="2 flippers"];
    Game -> Plunger [arrowtail=diamond,dir=both];
    Game -> Obstacle [label="obstáculos"];
    Ball -> TrajectoryController [label="delega"];
    TrajectoryController -> CollisionManager [label="delega"];
}'''
    return content


def run():
    DOCS.mkdir(exist_ok=True)
    pg,mapping=write_package_diagram()
    (DOCS/'packages_game.dot').write_text(pg,encoding='utf-8')
    (DOCS/'classes_game.dot').write_text(write_class_diagram(),encoding='utf-8')
    for stem in ('packages_game','classes_game'):
        for kind in ('png','svg'):
            try:
                subprocess.run(['dot',f'-T{kind}',str(DOCS/f'{stem}.dot'),'-o',str(DOCS/f'{stem}.{kind}')],
                               check=True,capture_output=True,text=True)
            except (OSError,subprocess.CalledProcessError) as e:
                print('Não foi possível gerar',stem,kind,':',e)
    (DOCS/'packages_game.mmd').write_text('flowchart LR\n'+''.join(
        f'  {a} --> {b}\n' for a,ds in mapping.items() for b in ds),encoding='utf-8')
    (DOCS/'classes_game.mmd').write_text('classDiagram\n'+
        '  Actuator <|-- Flipper\n  Actuator <|-- Plunger\n  Obstacle <|-- Bumper\n'+
        '  Obstacle <|-- Target\n  Obstacle <|-- Hole\n'+
        '  Game *-- Ball\n  Game *-- Flipper\n  Game *-- PlayerScore\n'+
        '  Ball --> TrajectoryController\n  TrajectoryController --> CollisionManager\n'+'  Stage *-- SpriteSheet\n',encoding='utf-8')
    (DOCS/'packages_game.puml').write_text('@startuml\n'+''.join(
        f'package {p} {{}}\n' for p in sorted(PACKAGE_NAMES))+
        ''.join(f'{src} --> {dst}\n' for src,ds in mapping.items() for dst in ds)+
        '@enduml\n',encoding='utf-8')
    (DOCS/'classes_game.puml').write_text('@startuml\n'
        'Actuator <|-- Flipper\nActuator <|-- Plunger\nObstacle <|-- Bumper\n'
        'Obstacle <|-- Target\nObstacle <|-- Hole\nGame *-- Ball\n'
        'Ball --> TrajectoryController\nTrajectoryController --> CollisionManager\nStage *-- SpriteSheet\n@enduml\n',encoding='utf-8')
    # Se pylint/pyreverse estiver disponível, ele tem prioridade na saída UML,
    # conforme a metodologia descrita no GDD original.
    if shutil.which('pyreverse'):
        for extension in ('png','svg'):
            try:
                subprocess.run(['pyreverse','-o',extension,str(MODULES),'-S','-k',
                                '-p','game','-d',str(DOCS)],check=True,
                               capture_output=True,text=True)
            except (OSError,subprocess.CalledProcessError) as err:
                print('pyreverse falhou; mantido diagrama Graphviz:',err)
    else:
        print('pyreverse nao instalado; diagramas gerados por AST e Graphviz.')
    print('Diagramas atualizados:',DOCS)


if __name__=='__main__':run()
