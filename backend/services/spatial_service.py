def get_row_words(words: list, ref_box: list, 
                  row_threshold: int = 15) -> str:
    """
    Get all words on the same horizontal row as ref_box,
    sorted left to right, joined as a single string.
    """
    ref_cy = (ref_box[1] + ref_box[3]) / 2
    
    row_words = []
    for w in words:
        b = w['box']
        cy = (b[1] + b[3]) / 2
        if abs(cy - ref_cy) <= row_threshold:
            row_words.append(w)
    
    # Sort left to right
    row_words.sort(key=lambda w: w['box'][0])
    
    return ' '.join(w['text'] for w in row_words)


def get_value_words(words: list, label_box: list,
                    row_threshold: int = 15) -> str:
    """
    Get all words on the same row as label_box
    that are to the RIGHT of the label box.
    """
    label_cx = (label_box[0] + label_box[2]) / 2
    label_cy = (label_box[1] + label_box[3]) / 2

    row_words = []
    for w in words:
        b = w['box']
        cy = (b[1] + b[3]) / 2
        cx = (b[0] + b[2]) / 2
        # Same row AND to the right of label
        if abs(cy - label_cy) <= row_threshold and cx > label_cx:
            row_words.append(w)

    # Sort left to right
    row_words.sort(key=lambda w: w['box'][0])
    return ' '.join(w['text'] for w in row_words)


def extract_fields(words: list, template: dict,
                   image_w: int = None,
                   image_h: int = None) -> dict:

    template_w = template.get('image_width', 1)
    template_h = template.get('image_height', 1)
    fields = template.get('fields', [])

    label_fields = {f['field_name']: f for f in fields
                    if f['field_type'] == 'label'}
    value_fields = [f for f in fields if f['field_type'] == 'value']

    if not words:
        return {vf['for_label']: '' for vf in value_fields}

    # Use actual image dimensions if provided
    # Otherwise estimate from word boxes
    if image_w and image_h:
        actual_w = image_w
        actual_h = image_h
    else:
        actual_w = max(w['box'][2] for w in words) * 1.05
        actual_h = max(w['box'][3] for w in words) * 1.05

    # Scale factors from template to current image
    scale_x = actual_w / template_w
    scale_y = actual_h / template_h

    print(f"Template size: {template_w}x{template_h}")
    print(f"Current image: {actual_w}x{actual_h}")
    print(f"Scale: x={scale_x:.3f} y={scale_y:.3f}")

    result = {}

    for vf in value_fields:
        tb = vf['box']
        print(f"Field '{vf['for_label']}': template box={tb}")

        field_name = vf['for_label']

        # Scale template value box to current image
        scaled_x1 = tb[0] * scale_x
        scaled_y1 = tb[1] * scale_y
        scaled_x2 = tb[2] * scale_x
        scaled_y2 = tb[3] * scale_y

        row_cy     = (scaled_y1 + scaled_y2) / 2
        row_height = max(scaled_y2 - scaled_y1, 10)

        # Tight vertical tolerance - half the row height
        v_tolerance = row_height * 0.7

        # Horizontal start - right edge of label in current image
        h_start = scaled_x1
        label_field = label_fields.get(field_name)
        if label_field:
            lb = label_field['box']
            h_start = lb[2] * scale_x  # label right edge scaled

        # Find matching words
        matched = []
        for w in words:
            b = w['box']
            cx = (b[0] + b[2]) / 2
            cy = (b[1] + b[3]) / 2
            if abs(cy - row_cy) > v_tolerance:
                continue
            if cx < h_start:
                continue
            matched.append(w)

        matched.sort(key=lambda w: w['box'][0])
        result[field_name] = ' '.join(
            w['text'] for w in matched
        ) if matched else ''

    return result
