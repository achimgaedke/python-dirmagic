import dirmagic

# print(list(dirmagic.iter_projects("..", dirmagic.project_types.is_python_project)))

print(list(dirmagic.identify_project(".")))