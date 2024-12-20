import cv2
import numpy as np

def check(rect1,rect2):
      """
      检查两个轮廓是否重叠
      通过判断两个轮廓的外接矩形是否有重叠来间接判断轮廓是否有重叠
      """
      x1,y1,w1,h1=rect1
      x2,y2,w2,h2=rect2
      return not(x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)
canvas=np.ones((800,800,3),dtype=np.uint8)*255#绘制白布
colors = [0, 1, 2, 3, 4, 5 ,6]
actual_colors = [(0, 0, 255), (0, 225, 0), (255, 0, 0), (150, 0, 0), (80, 250, 0),(0,25,0),(0,0,20)]#定义颜色

shapes=[cv2.CHAIN_APPROX_NONE,cv2.CHAIN_APPROX_SIMPLE]
drawn_rect=[]

#用于存储绘制完的图形后的边缘图像
edge_images=[]

#for i in range(12):
while len(drawn_rect)<=10:    
    # 随机选择形状
        shape_type = np.random.choice(shapes)
    # 随机选择颜色
    
        color_indices = np.random.choice(colors)
        color=actual_colors[color_indices]
        
    # 随机选择左上角坐标
        x = np.random.randint(0, 800-50)
        y = np.random.randint(0, 800-50)
    # 随机选择图形大小
        size = np.random.randint(20, 80)
    # 随机选择绘制圆形、矩形或三角形
        shape = np.random.randint(0, 3)
    
    
        if shape == 0:#绘制圆形
           cv2.circle(canvas, (x + size // 2, y + size // 2), size // 2, color, -1)
        
        elif shape == 1:#绘制矩形
           cv2.rectangle(canvas, (x, y), (x + size, y + size), color, -1)
        

        elif shape == 2:#绘制三角形
           pts = np.array([[x, y], [x + size, y], [x + size // 2, y + size]], np.int32)
           cv2.fillPoly(canvas, [pts], color)
         
    # 获取新绘制图形的轮廓
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 10, 120)
        white_edges = np.ones_like(gray) * 255
        white_edges[edges > 0] = 0#将在edges图像中检测到边缘的位置对应的像素值设为 0（黑色）
        edge_images.append(white_edges)
        #查找轮廓
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.RETR_EXTERNAL表示只检测外轮廓，
        # cv2.CHAIN_APPROX_SIMPL表示压缩水平、垂直和对角线段，只保留端点
        
        #检查重叠
        overlap=False
        if not False:
            for contour in contours:
                x,y,w,h=cv2.boundingRect(contour)
                rect=(x,y,w,h)
            drawn_rect.append(rect)
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                rect = (x, y, w, h)
                for drawn in drawn_rect:
                    if check(drawn,rect):
                        overlap=True
                        break
                if overlap:
                    break    
            
cv2.imshow("shapes", canvas)
cv2.imwrite("shapes.png",canvas)
cv2.waitKey(0)
#cv2.destroyAllWindows()
cv2.imshow("edges",edge_images[-1])
cv2.imwrite("edges.png",edge_images[-1])
cv2.waitKey(0)
# cv2.destroyAllWindows()               

#绘制轮廓检测图像
cv2.drawContours(canvas, contours, -1, (255, 150, 150), 2)#在原图上标注轮廓
cv2.imshow("contours",canvas)
cv2.imwrite("contours.png",canvas)
cv2.waitKey(0)
#cv2.destroyAllWindows()

#打印图形个数
num_shapes = len(drawn_rect)
print("图形数量",num_shapes)

#模型匹配
rect_start=(1,1)
rect_end=(1,1)
def draw_rectangle(event,x,y,flags,param):
    """鼠标回调函数，用于获取鼠标选取的矩形"""
    global rect_start,rect_end
    if event==cv2.EVENT_LBUTTONDOWN:
        rect_start=(x,y)
    elif event==cv2.EVENT_LBUTTONUP:
        rect_end=(x,y)
        cv2.rectangle(param[0], rect_start, rect_end, (0, 255, 0), 2)
image=cv2.imread("shapes.png")
clone=image.copy()
cv2.namedWindow('main_windows')
cv2.setMouseCallback('main_windows',draw_rectangle,[image])

while True:
    cv2.imshow('main_windows',image)
    key=cv2.waitKey(1) & 0xFF
    
    if key==ord('r'):
        image=clone.copy()
        rect_start = (-1, -1)
        rect_end = (-1, -1)
        # 重新设置鼠标回调函数，确保能ima再次正常绘制矩形框
        cv2.setMouseCallback('main_windows', draw_rectangle)
    elif key==ord('s'):
        cv2.imwrite("template.png",image)    
    elif key==13:
        if rect_start!=(-1,-1) and rect_end!=(-1,-1):
            x1, y1 = min(rect_start[0], rect_end[0]), min(rect_start[1], rect_end[1])
            #计算矩形左上角坐标
            x2, y2 = max(rect_start[0], rect_end[0]), max(rect_start[1], rect_end[1])
            #计算矩形右下角坐标
            template = clone[y1:y2, x1:x2]#从clone提取用户选择的矩形区域作为模板
            w, h = template.shape[:2]#获取模板高度与宽度

            result = cv2.matchTemplate(clone, template, cv2.TM_CCOEFF_NORMED)#在clone上进行模板匹配
            threshold = 0.8#设置匹配的阈值
            loc = np.where(result >= threshold)#获取匹配结果大于等于阈值的位置
            #绘制匹配结果
            for pt in zip(*loc[::-1]):#遍历匹配结果的每个位置
                cv2.rectangle(clone, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

            cv2.imshow('matching.png', clone)
            cv2.imwrite("matching.png",clone)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            image=clone.copy()#将clone复制回image,更新显示的图像
            rect_start=(-1,-1)#重置矩形的起始点与结束点
            rect_end=(-1,-1)
    elif key==ord('q'):
        break
cv2.destroyAllWindows()            



