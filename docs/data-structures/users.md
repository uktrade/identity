# Users

The ID service uses a minimal custom Django User extended from `AbstractBaseUser`. We import the model via `django.contrib.auth.get_user_model`.

It uses `sso_email_id` as the primary key (so `user.pk` works but `user.id` does not).

We also use the default flags `is_active`, `is_staff` and `is_superuser` but no other information is stored against the User model; instead all names, emails and other details are stored against the relevant [Profile](./profiles.md).
