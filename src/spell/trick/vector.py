from spell.blunders import Blunder
from spell.fragments import Pattern,VectorFragment,NumberFragment
from spell.trick.tricks import Trick
from spell.execution import Context
import math
merge_vector = Trick(Pattern.of(1, 3, 4, 5, 1, 4, 7),"Absorption Distortion")
@merge_vector()
def origin_vector(ctx: Context):
    return VectorFragment()
@merge_vector(NumberFragment)
def x_vector(ctx: Context,x: NumberFragment):
    return VectorFragment(x)
@merge_vector(NumberFragment,NumberFragment)
def xy_vector(ctx: Context,x: NumberFragment,y: NumberFragment):
    return VectorFragment(x,y)
@merge_vector(NumberFragment,NumberFragment,NumberFragment)
def xyz_vector(ctx: Context,x: NumberFragment,y: NumberFragment,z: NumberFragment):
    return VectorFragment(x,y,z)
magnitude = Trick(Pattern.of(3, 4, 5, 2, 4, 1), "Magnitude Distortion")
@magnitude(VectorFragment)
def get_magnitude(ctx: Context,vector: VectorFragment):
    return math.sqrt((vector.x**2)+(vector.y**2)+(vector.z**2))
normalize = Trick(Pattern.of(3, 4, 5, 6, 3),"Regularity Distortion")
@normalize(VectorFragment)
def get_normal(ctx:Context,vector: VectorFragment):
    mag = get_magnitude(ctx,vector)
    return VectorFragment(vector.x/mag,vector.y/mag,vector.z/mag)
x_trick = Trick(Pattern.of(0,3,6),"Primary Distortion")
@x_trick(VectorFragment)
def get_x(ctx:Context,vector: VectorFragment) -> NumberFragment:
    return NumberFragment(vector.x)
y_trick = Trick(Pattern.of(0,4,7),"Secondary Distortion")
@y_trick(VectorFragment)
def get_y(ctx:Context,vector: VectorFragment) -> NumberFragment:
    return NumberFragment(vector.y)
z_trick = Trick(Pattern.of(0,5,8),"Secondary Distortion")
@z_trick(VectorFragment)
def get_z(ctx:Context,vector: VectorFragment) -> NumberFragment:
    return NumberFragment(vector.z)