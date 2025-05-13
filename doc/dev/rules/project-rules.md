# Porject About

1. Tooling

    a. Ppoetry

    The package is managed by poetry, this means:

        poetry add <package>
        poetry add <package> --with=-dev #= for dev deps

    b. Linting:

    The project uses pre-commit for runnign rules, check with:

        pre-commit run

    The most common error is writing lines > 90 characters
