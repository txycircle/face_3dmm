# -*- coding: utf-8 -*-
# @Time    : 2021/8/7 14:15
# @Author  : xinyuan tu
# @File    : one_generate_image.py
# @Software: PyCharm
import numpy as np
import os
import tqdm
from PIL import Image
from example.utils import *
from Render.Render import *
from Render.Zbuffer import *
from Render.Projection import *


def main():
    modelconfig = ModelConfig()
    shapePC, expPC, texPC, shapeMU, texMU, \
    LandmarksCorrespondence, Tri, VertexTri, skinmask_idx, point_one_ring = Load3dmmPara(modelconfig.base_bfm)
    lightMU = np.load(modelconfig.LightMU)
    lightconv = np.load(modelconfig.Lightcov)

    if not os.path.isdir(modelconfig.image_path):
        os.makedirs(modelconfig.image_path)


    ########生成3DMM SHAPE########
    shape_para = np.random.rand(1, shapePC.shape[1])
    Shape = shapeMU + np.dot(shape_para, shapePC.T)
    exp_para = 2 * np.random.rand(1, expPC.shape[1]) - 1
    Shape = Shape + np.dot(exp_para, expPC.T)
    Shape = Shape.reshape(int(Shape.shape[1] / 3), 3)
    Shape = Shape - np.mean(Shape, axis=0, keepdims=True)
    Shape = Shape.T

    ########生成3DMM TEXTURE########
    texture_para = 4 * np.random.rand(1, texPC.shape[1]) - 2
    texture = texMU + np.dot(texture_para, texPC.T)
    texture = texture.reshape(int(texture.shape[1] / 3), 3)

    # ########生成3DMM LIGHT########
    # light_para = 6 * np.random.rand(9, 1) - 4
    # light = (np.expand_dims(lightMU, -1) + np.dot(lightconv, light_para)) / 5

    ########PROJECTION########
    angle = np.zeros((1, 3))
    T = np.expand_dims([0, 0, 10], 1)
    Shape_2d = projection(Shape, modelconfig.imagesize, angle,T)



    ######Zbuffer#######
    tranfer = Zbuffer(np.transpose(Shape_2d), Tri,  modelconfig.imagesize)
    barycentric_coordinates, triangle_ids, zbuffer = tranfer.forward()


    ######render color#######
    rander = Render_color(barycentric_coordinates, triangle_ids, texture, Tri, modelconfig.imagesize)
    image = rander.forward()

    img = Image.fromarray(np.uint8(image))
    img.show()
    image_path = os.path.join(modelconfig.image_path,  'A.jpg')
    img.save(image_path)


if __name__=="__main__":
    main()