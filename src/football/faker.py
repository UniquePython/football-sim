import faker

from .nationality import Nationality

fakers: dict[Nationality, faker.Faker] = {
    nationality: faker.Faker(locale=nationality.locale) for nationality in Nationality
}
