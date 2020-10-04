def dict2hcl(d, tabs=4, only_values=False):
    '''Convert dictionary to HCL map type.
    '''
    result = '''{
%s
}'''
    maps = []
    for k, v in d.items():
        maps += [" " * tabs + "\"%s\" = \"%s\"," % (k, v)]
    key_values = '\n'.join(maps)
    return result % key_values if not only_values else key_values
