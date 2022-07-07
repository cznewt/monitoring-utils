
def split_by_keyword(query, split_keywords, level=0):
    if level < len(split_keywords):
        new_query = []
        for item in query:
            new_query = new_query + item.split(split_keywords[level])
        return split_by_keyword(new_query, split_keywords, level + 1)

    else:
        return query


def clean_comments(query):
    lines = query.splitlines()
    output_lines = []
    for line in lines:
        line = line.strip()
        if not line.startswith("#"):
            output_lines.append(line)
    return " ".join(output_lines)
