# PostgreSQL с готовым скриптом создания таблиц
FROM postgres:16-alpine

# Файлы из этой папки выполняются автоматически при первом создании базы
COPY init.sql /docker-entrypoint-initdb.d/init.sql

# Проверка по TCP (-h 127.0.0.1): контейнер становится "healthy" только после полной
# инициализации (во время неё временный сервер слушает лишь unix-сокет)
HEALTHCHECK --interval=5s --timeout=5s --start-period=30s --retries=10 \
  CMD pg_isready -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" || exit 1
