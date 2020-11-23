from app.bd_helper.bd_helper import add_user, validate_user, get_user, edit_user, delete_user, add_presentation, \
    get_presentation, delete_presentation, create_check, add_check, get_check, delete_check

user = add_user("milty", "12345")
print("Created user: " + str(user))
user = add_user("milty", "12345")
print("User with same params: " + str(user))

valid = validate_user("milty", "12345")
print("Validated user: " + str(valid))

user = get_user("milty")
print("User got: " + str(user))

user.is_admin = True
edited = edit_user(user)
print("User edited: " + str(edited))
user = get_user("milty")
print("User got: " + str(user))


print("User has " + str(len(user.presentations)) + " presentations")

presentation_name = "New presentation"
user, presentation = add_presentation(user, presentation_name)
print("Presentation created: " + str(presentation))

print("User has " + str(len(user.presentations)) + " presentations")
for presentation_id in user.presentations:
    presentation = get_presentation(presentation_id)
    print("Presentation got: " + str(presentation))

    if presentation.name == presentation_name:
        checks = create_check(conclusion_slide='1, 3', probe_slide='7, 11')
        print("Checks created: " + str(checks))

        presentation, checks = add_check(presentation, checks)
        print("Checks added: " + str(checks))

        print("Presentation has " + str(len(presentation.checks)) + " checks")
        for checks_id in presentation.checks:
            checks = get_check(checks_id)
            print("Checks got: " + str(checks))

            presentation, checks = delete_check(presentation, checks_id)
            print("Checks deleted: " + str(checks))

    print("Presentation has " + str(len(presentation.checks)) + " checks")

    user, presentation = delete_presentation(user, presentation_id)
    print("Presentation deleted: " + str(presentation))

print("User has " + str(len(user.presentations)) + " presentations")


user = delete_user("milty")
print("Deleted user: " + str(user))
user = get_user("milty")
print("User got: " + str(user))
