from .base import find_value_near_label, full_text, regex_find


def _add_if_found(output: dict, key: str, value: str | None) -> None:
    if value:
        output[key] = value


def extract_birth_cert(ocr_results) -> dict:
    text = full_text(ocr_results)
    fields = {}

    _add_if_found(fields, "registration_date", find_value_near_label(ocr_results, ["REGISTRATION DATE"]))
    _add_if_found(fields, "issuance_date", find_value_near_label(ocr_results, ["ISSUANCE DATE"]))
    _add_if_found(fields, "registration_office", find_value_near_label(ocr_results, ["REGISTRATION OFFICE"], collect_tokens=4))

    birth_reg_no = find_value_near_label(ocr_results, ["BIRTH REGISTRATION NUMBER"], collect_tokens=1)
    birth_reg_no = birth_reg_no or regex_find(text, r"\b\d{17}\b")
    _add_if_found(fields, "birth_reg_no", birth_reg_no)

    dob = find_value_near_label(ocr_results, ["DATE OF BIRTH", "Date of Birth"], collect_tokens=3)
    dob = dob or regex_find(
        text,
        r"\b\d{1,2}\s+(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+\d{4}\b",
    )
    _add_if_found(fields, "dob", dob)

    sex = find_value_near_label(ocr_results, ["SEX", "Sex"], collect_tokens=1)
    sex = sex or regex_find(text, r"\b(MALE|FEMALE)\b")
    _add_if_found(fields, "sex", sex)

    _add_if_found(fields, "name_bn", find_value_near_label(ocr_results, ["নিবন্ধিত ব্যক্তির নাম"]))
    _add_if_found(fields, "name_en", find_value_near_label(ocr_results, ["REGISTERED PERSON NAME"], collect_tokens=4))
    _add_if_found(fields, "birth_place_bn", find_value_near_label(ocr_results, ["জন্মস্থান"]))
    _add_if_found(fields, "birth_place_en", find_value_near_label(ocr_results, ["PLACE OF BIRTH"], collect_tokens=3))
    _add_if_found(fields, "mother_name_bn", find_value_near_label(ocr_results, ["মাতার নাম"]))
    _add_if_found(fields, "mother_name_en", find_value_near_label(ocr_results, ["MOTHER'S NAME", "Mother's Name"], collect_tokens=4))
    _add_if_found(fields, "mother_nationality", find_value_near_label(ocr_results, ["মাতার জাতীয়তা", "MOTHER'S NATIONALITY"]))
    _add_if_found(fields, "father_name_bn", find_value_near_label(ocr_results, ["পিতার নাম"]))
    _add_if_found(fields, "father_name_en", find_value_near_label(ocr_results, ["FATHER'S NAME", "Father's Name"], collect_tokens=4))
    _add_if_found(fields, "father_nationality", find_value_near_label(ocr_results, ["পিতার জাতীয়তা", "FATHER'S NATIONALITY"]))

    return fields
