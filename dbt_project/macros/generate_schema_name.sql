{% macro generate_schema_name(custom_schema_name, node) -%}
    {#- Schéma = exactement le custom_schema configuré (staging/intermediate/marts),
        pas "<schéma cible>_<custom_schema>" : des schémas lisibles pour parcourir
        la base (et la configurer comme source Metabase) sans préfixe technique. -#}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
