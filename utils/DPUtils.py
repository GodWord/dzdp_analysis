# -*- coding:utf-8 -*-


class DPUtils:
    @staticmethod
    def get_real_by_tag(tags, css_and_px_dict, svg_threshold_and_int_dict, font_size=12, diff=0):
        import math
        result = ''
        for tag in tags:
            # 如果是字符，则直接取出
            if isinstance(tag, str):
                result += tag
            else:
                # 如果是span类型，则要去找数据
                # span class的attr
                span_class_attr_name = tag.attrs["class"][0]
                # 偏移量，以及所处的段
                offset, position = css_and_px_dict[span_class_attr_name]
                index = abs(int(float(offset)))
                position = abs(int(float(position)))
                # 判断
                for key, value in svg_threshold_and_int_dict.items():
                    if position in value:
                        threshold = int(math.ceil(index / font_size))
                        word = key[threshold + diff]
                        result += word
        return result
