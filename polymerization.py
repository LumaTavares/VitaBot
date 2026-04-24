def compair_position(xmin,ymin,xmax,ymax  ,  xmin2,ymin2,xmax2,ymax2):
  cordenada1 = (xmin, ymin , xmax, ymax)
  cordenada2 = (xmin2, ymin2 , xmax2, ymax2)
  area1 = (xmax - xmin) * (ymax - ymin)
  area2 = (xmax2 - xmin2) * (ymax2 - ymin2)
  inter_xmin = max(xmin, xmin2)
  inter_ymin = max(ymin, ymin2)
  inter_xmax = min(xmax, xmax2)
  inter_ymax = min(ymax, ymax2)

  if inter_xmax < inter_xmin or inter_ymax < inter_ymin:
    return 0

  inter_area = (inter_xmax - inter_xmin) * (inter_ymax - inter_ymin)
  iou = inter_area / (area1 + area2 - inter_area)
  if iou > 0.5:
    return 1
  return 0