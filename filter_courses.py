def units_to_value(l):
    try:
        s = 0
        for v in l:
            s += int(v)
        return s
    except:
    # case "Units arranged"
        return -1

def filter_courses(df, grad=False):
    print(df.shape)
    # Exclude courses in EECS (Course 6) and Aero Astro (Course 16)
    df = df[df['course_id'] != '6']
    print(df.shape)
    df = df[df['course_id'] != '16']
    print(df.shape)
    # Exclude courses whose units sum to less than 12
    df['units'] = [units_to_value(d.split()[0].split('-')) for d in list(df.hours)] 
    df = df[df['units'] >= 12]
    if grad:
        # Exclude courses that are not grad courses
        df['grad'] = [d.strip('[\'').split(' ')[0] == 'G' for d in list(df.terms)]
        df = df[df['grad'] == True]
    print(df.shape)
    return df
    
def filter_search(df, course_numbers):
    df['keep'] = [x in course_numbers for x in list(df.course_number)]
    df = df[df['keep'] == True].filter(list(df.columns)[:-1])
    print(df.shape)
    return df
