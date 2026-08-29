# Data-flow analyst — detection patterns

> Reference doc for `data-flow-analyst`. Read at runtime once `stack.json`
> has been consulted, to know which language/library patterns to grep for
> in each of the five categories (database, external APIs, file I/O,
> environment variables, configuration sources).

The agent body owns the decision logic (which categories run, how to
classify findings, when to stop). This doc is the pattern catalogue only.

---

## 1. Database access

| Language / library | Patterns |
|---|---|
| python (sqlalchemy) | `Session`, `sessionmaker`, `create_engine`, `select(`, `Query(`, `declarative_base`, `Base.metadata`, `Mapped[`, `Column(` |
| python (raw sql) | `cursor.execute(`, `connection.execute(`, multi-line triple-quoted strings containing `SELECT`/`INSERT`/`UPDATE`/`DELETE` |
| python (other ORM) | `peewee.Model`, `tortoise.models.Model`, `pony.orm.Database`, `django.db.models.Model` |
| python (drivers) | `psycopg2.connect(`, `pymysql.connect(`, `pymongo.MongoClient(`, `redis.Redis(`, `asyncpg.connect(`, `aiomysql.connect(` |
| java/kotlin (jpa) | `@Entity`, `@Table`, `@Column`, `@OneToMany`/`@ManyToOne`, `EntityManager`, `JpaRepository`, `CrudRepository`, `@Query` |
| java (jdbc) | `DataSource`, `JdbcTemplate.query/update/execute`, `Connection.prepareStatement`, `ResultSet` |
| java (jooq) | `DSLContext`, `Tables.`, `dsl().select(...).from(...)` |
| kotlin (exposed) | `Table` extends; `transaction { ... }`; `Op`/`select { }` |
| go | `database/sql` `db.Query/Exec/QueryRow`; `gorm` `db.Find/Create/Save`; `sqlx`; `pgx.Connect` |
| rust (sqlx) | `sqlx::query!`, `sqlx::query_as!`, `sqlx::PgPool::connect`, `Pool<Postgres>` |
| rust (diesel) | `#[derive(Queryable, Insertable)]`, `diesel::insert_into`, `users::table.filter(...)` |
| rust (sea-orm) | `Entity::find()`, `ActiveModel` |
| csharp (ef-core) | `DbContext`, `DbSet<T>`, `db.Entity.Where(...).ToListAsync()`, `[Table]`, `[Column]`, `Migration` |
| csharp (dapper) | `IDbConnection.Query<T>(...)`, `Execute(...)`, `QueryFirstAsync` |
| ruby (rails) | `ActiveRecord::Base`; `Model.where`/`find`/`create!`/`update!`; migrations under `db/migrate/` |
| ruby (sequel) | `Sequel::Model`, `DB[:table]` |
| php (eloquent) | `class X extends Model`, `User::where()->first()`, `$user->save()` |
| php (doctrine) | `#[ORM\Entity]`, `EntityManager`, `Repository::findOneBy` |
| php (raw) | `\PDO::prepare`, `mysqli_query` |
| typescript (prisma) | `prisma.user.findMany`, `await prisma.$queryRaw` |
| typescript (typeorm) | `@Entity`, `getRepository`, `dataSource.manager` |
| typescript (drizzle) | `drizzle().select().from(...)` |
| typescript (mongoose) | `mongoose.Schema`, `model.find` |
| typescript (raw) | `pg.Pool`, `mysql.createConnection`, `mongodb.MongoClient` |

For each finding: file, line, table/entity (if identifiable), operation
(R / W / DDL), language.

---

## 2. External APIs (HTTP libraries)

| Language / library | Patterns |
|---|---|
| python | `requests.get/post/put/delete/patch/head`; `httpx.AsyncClient/Client/.get/.post`; `aiohttp.ClientSession`; `urllib.request.urlopen`, `urllib3.PoolManager` |
| java/kotlin | `RestTemplate.getForObject/postForObject`, `WebClient.get().uri()...retrieve()`, `OkHttpClient.newCall`, `HttpClient.newHttpClient()` (java.net) |
| kotlin (ktor client) | `HttpClient { }`, `client.get/post` |
| go | `http.Get`, `http.Post`, `(*http.Client).Do(req)` |
| rust | `reqwest::Client::new()`, `reqwest::get(...).await` |
| csharp | `HttpClient`, `httpClient.GetAsync/PostAsync/SendAsync`; refit `RestService.For<>` |
| ruby | `Net::HTTP.get/post`, `HTTParty.get/post`, `Faraday.new(...)` |
| php | `Guzzle\\Client`, `\\GuzzleHttp\\Client`, `curl_init`/`curl_exec`, `file_get_contents("http://...")` |
| typescript / javascript | `fetch(`, `axios.get/post/put/delete`, `ky.get`, `request(`, `got.get` |

For each call: extract URL pattern (literal or env var), HTTP method,
file:line, auth header source (env var, header dict), language.

---

## 3. File I/O

| Language / library | Patterns |
|---|---|
| python | `open(`, `Path(...).read_text/read_bytes/write_text/write_bytes`, `Path(...).open(`, `csv.reader/writer`, `json.load/loads/dump/dumps`, `pickle.load/dump`, `yaml.safe_load/dump`, `pandas.read_csv/read_parquet/to_csv/to_parquet` |
| java/kotlin | `Files.readString/readAllBytes/write/writeString`, `BufferedReader`, `FileInputStream`, `FileWriter`, `Paths.get(...)`, Jackson `ObjectMapper.read/writeValue` |
| go | `os.Open`, `os.ReadFile`, `os.WriteFile`, `bufio.NewScanner`, `encoding/json.Unmarshal/Marshal`, `csv.NewReader/Writer` |
| rust | `std::fs::read_to_string`, `std::fs::write`, `tokio::fs::read_to_string`, `serde_json::from_str/to_string`, `serde_yaml::*` |
| csharp | `File.ReadAllText/WriteAllText`, `StreamReader`, `JsonSerializer.Deserialize/Serialize`, `XmlSerializer` |
| ruby | `File.open`, `File.read`, `File.write`, `CSV.read`, `JSON.parse/generate`, `YAML.load_file` |
| php | `file_get_contents`, `file_put_contents`, `fopen`/`fread`/`fwrite`, `json_decode`/`json_encode`, `yaml_parse_file` |
| typescript / javascript | `fs.readFileSync/writeFileSync`, `fs/promises.readFile/writeFile`, `JSON.parse/stringify`, `papaparse`, `js-yaml` |

Distinguish reads vs writes. Distinguish purpose (config / data /
output / log).

---

## 4. Environment variables

| Language | Patterns |
|---|---|
| python | `os.environ[`, `os.environ.get(`, `os.getenv(`, `dotenv.load_dotenv(`, `pydantic_settings.BaseSettings` subclasses |
| java/kotlin | `System.getenv(...)`, `@Value("${...}")` (Spring), `@ConfigurationProperties` (Spring); `System.getProperty(...)` |
| go | `os.Getenv("...")`, `os.LookupEnv("...")`, `envconfig.Process(...)` (kelseyhightower) |
| rust | `std::env::var("...")`, `dotenvy::dotenv()`, `envy::from_env::<Config>()` |
| csharp | `Environment.GetEnvironmentVariable("...")`, `IConfiguration.GetValue/GetSection`, `IOptions<T>` |
| ruby | `ENV["..."]`, `ENV.fetch("...")`, `dotenv-rails` |
| php | `getenv('...')`, `$_ENV['...']`, `env('...')` (Laravel), `\Symfony\Component\Dotenv\Dotenv` |
| typescript / javascript | `process.env.VAR`, `dotenv.config()`, `import.meta.env.VAR` (Vite), `env-var.get(...)` |

List every env var name accessed.

---

## 5. Configuration sources

| Language / framework | Config sources |
|---|---|
| any | `.env`, `.env.example`, `.env.*` |
| python | `config.yaml/toml/json`, `settings.py`, `settings.ini`, `pyproject.toml [tool.<app>]`, `configparser` |
| java/kotlin (spring) | `application.yaml`/`application.yml`/`application.properties`, profile-specific variants (`application-prod.yml`) |
| java/kotlin (other) | `META-INF/microconfig.yaml` (Micronaut), `application.properties` (Quarkus) |
| go | `config.yaml`/`toml`, `viper.ReadInConfig` |
| rust | `config.toml`/`yaml`, `figment::Figment::from(...)` |
| csharp | `appsettings.json`, `appsettings.{Environment}.json`, `web.config` (legacy) |
| ruby (rails) | `config/application.rb`, `config/database.yml`, `config/credentials.yml.enc`, `config/initializers/*.rb` |
| php (laravel) | `config/*.php`, `.env` |
| php (symfony) | `config/packages/*.yaml`, `config/services.yaml` |
| typescript / javascript | `tsconfig.json` (build), `package.json` "config", `next.config.{js,ts}`, `nuxt.config.ts`, framework-specific config |

For each: format, what loads it, where the loaded values are used.
