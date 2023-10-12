from ursina import Ursina,Entity,Sky,Vec2,DirectionalLight,Vec3,window,Text,Texture,mouse,distance,math,Keys,Audio,Animator,color,Button,Func,Sequence,Wait,camera,sys,application
import random
from PIL import Image
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
import time

class Player(FirstPersonController):
    def __init__(self,parent, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.collider = 'box'
        self.gravity = True
        self.collider='box'

class Sene(Entity):
    def __init__(self,parent = None , add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities, **kwargs)

        bg_music = Audio("nm.mp3")
        bg_music.volume = 0.4  
        bg_music.loop=True
        bg_music.play()
        #--------decorations-------------
        Entity(model='cube',position=(25,2,0),scale_z=50,scale_y=4,collider='box',texture='brick',texture_scale=Vec2(3))
        Entity(model='cube',position=(-25,2,0),scale_z=50,scale_y=4,collider='box',texture='brick',texture_scale=Vec2(3))
        Entity(model='cube',position=(0,2,25),scale_x=50,scale_y=4,collider='box',texture='brick',texture_scale=Vec2(3))
        Entity(model='cube',position=(0,2,-25),scale_x=50,scale_y=4,collider='box',texture='brick',texture_scale=Vec2(3))
        large_rock = Entity(model='assets/large_rock.glb',scale=8,position=(random.randint(-20,20),1.7,random.randint(-20,20)),collider='box')
        Entity(model='assets/rock.glb',scale=4,position=(random.randint(-20,20),0.5,random.randint(-20,20)),collider='box')
        Entity(model='assets/bird.glb',scale=1,position=(25,4.2,0))
        #xxxxxxxxdecorations eddxxxxxxxxx

        self.score=0
        self.text_entity = Text(str(self.score), world_scale=30,origin=(0,-12,0))
        self.ground = Entity(parent=self,model='plane',scale=50,texture=Texture(Image.open('assets/grass_texture.jpg').convert('RGBA')),texture_scale=Vec2(32),collider='box')
        self.player=Player(parent=self)
        self.bin = Entity(parent=self,model='assets/bin',scale=40,collider='box',position=(10,0,0))
        self.waste_list=[]
        self.selected=[]
        for i in range(random.randint(10,20)):
            waste=Entity(parent=self,model=random.choice(['assets/can.glb','assets/lipstic.glb','assets/skull.glb']),scale=1,collider='box')
            waste.rotation_y=random.randint(0,180)
            self.selected.append(False)
            waste.position=(random.uniform(-20,20), 0.1, random.uniform(-20, 20))
            self.waste_list.append(waste)
        self.entity_selected=None
    def update(self):
        if self.score == len(self.waste_list):
            application.quit()
        if self.score==len(self.waste_list)-1 and len(self.text_entity.text)<3:
            self.text_entity.text = self.text_entity.text+' ONE MORE TO GO !! Finish your work and go HOME'
        if mouse.hovered_entity in self.waste_list :
            index = self.waste_list.index(mouse.hovered_entity)
            entity = self.waste_list[index]
        if self.entity_selected is not None and distance(self.entity_selected,self.player)<=3:
                player_position = self.player.position
                player_rotation = self.player.rotation_y
                offset_distance = 1.0  
                offset_x = offset_distance * math.sin(math.radians(player_rotation))
                offset_z = offset_distance * math.cos(math.radians(player_rotation))
                
                self.entity_selected.position = (player_position.x + offset_x+0.5, player_position.y + 0.8, player_position.z + offset_z+0.9)

                if self.entity_selected.intersects(self.bin).hit:
                    dustbin_music = Audio("dustbin.mp3")
                    dustbin_music.volume=0.8
                    self.entity_selected.disable()
                    self.entity_selected=None
                    self.score+=1
                    self.text_entity.text = str(self.score)
                    dustbin_music.play()
    def input(self,key):
        if mouse.hovered_entity in self.waste_list and key==Keys.left_mouse_down:
            index = self.waste_list.index(mouse.hovered_entity)
            entity = self.waste_list[index] 
            self.selected[index]=True  
            if distance(entity,self.player)<=3:
                pickup_music = Audio("pickup.mp3")
                pickup_music.volume=0.8
                self.entity_selected = entity  
                pickup_music.play()


class MenuButton(Button):
    def __init__(self,text='',radius=0.1,**kwargs):
        super().__init__(text,radius,scale=(0.25,0.075),highlight_color=color.azure,**kwargs)
        for key,value in kwargs.items():
            setattr(self,key,value)
class ParentMenu(Entity):
    def __init__(self, add_to_scene_entities=True, **kwargs):
        super().__init__(add_to_scene_entities, **kwargs)
        self.parent = camera.ui
        self.y = 0.15
class MainMenu:
    def __init__(self,own_instance,state_handler,parent) -> None:
        self.p = parent
        button_spacing = 0.075*1.25
        own_instance.buttons=[
            MenuButton('start',on_click=self.start_game),
            MenuButton('quit', on_click=Sequence(Wait(.01), Func(sys.exit))),
        ]
        for i,e in enumerate(own_instance.buttons):
            e.parent = own_instance
            e.y=(-i-1)*button_spacing
    def start_game(self):
        self.p.enabled=False
        Entity.default_shader = lit_with_shadows_shader
        DirectionalLight().look_at(Vec3(1,-1,-1))
        Sene()
        Sky()

class App(Ursina):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        window.title='GoodBoy'
        window.icon = 'assets/boy.ico'
        window.borderless=False
        window.exit_button.enabled=False
        window.cog_button.enabled=False
        window.fps_counter.enabled=False
        window.show_ursina_splash=True

        parent_menu = ParentMenu()
        main_menu = Entity(parent = parent_menu)
        self.state_handler=Animator({
            'main_menu':main_menu
        })
        MainMenu(main_menu,self.state_handler,parent=parent_menu)
        background = Entity(parent=parent_menu, model='quad', texture='grass', scale=(camera.aspect_ratio,1), color=color.white, z=1, world_y=0)

app=App()
app.run()