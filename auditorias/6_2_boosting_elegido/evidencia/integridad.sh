#!/bin/sh
# Comprueba que la auditoría no modificó el proyecto (Regla 1 de la Skill).
# Ejecutar desde la raíz del proyecto. Requiere la huella previa en
# /tmp/claude-0/auditoria_6_2/md5_antes.txt y el respaldo en /tmp/claude-0/auditoria_6_2/respaldo/.
B=/tmp/claude-0/auditoria_6_2
echo "Huella MD5 de datos/credit_g.csv (RESUMEN.md declara 19d37d4238836d135ab13d73dc42d5e4):"
md5sum datos/credit_g.csv
find . -path ./.git -prune -o -path ./auditorias -prune -o -type f -print0 | sort -z | xargs -0 md5sum > $B/md5_despues.txt
echo "Archivos comparados (fuera de .git/ y auditorias/): $(wc -l < $B/md5_despues.txt)"
if diff $B/md5_antes.txt $B/md5_despues.txt; then echo "Proyecto sin cambios: True"; else echo "Proyecto sin cambios: False"; fi
for d in resultados figs evidencia; do
  if diff -r $B/respaldo/$d $d > /dev/null; then echo "$d/ igual al respaldo: True"; else echo "$d/ igual al respaldo: False"; fi
done
echo "__pycache__ en el proyecto: $(find . -name __pycache__ -not -path './.git/*' | wc -l)"
