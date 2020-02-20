def unique_slug_generator(name, class_name):
    slug = name.replace(" ", "-").lower()
    unique_slug = slug
    num = 1
    while class_name.objects.filter(slug=unique_slug).exists():
        unique_slug = '{}-{}'.format(slug, num)
        num += 1
    return unique_slug
