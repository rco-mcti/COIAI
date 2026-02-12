<#
.SYNOPSIS
    Script PowerShell para remover arquivos .docx e .pdf do histórico Git.
    BASEADO NO DOCUMENTO FORNECIDO PELO USUÁRIO.

.DESCRIPTION
    Este script utiliza a ferramenta 'git-filter-repo' (instalada via pip) para reescrever
    o histórico do Git, removendo permanentemente arquivos com extensões .docx e .pdf.
    
    FLUXO:
    1. Instala git-filter-repo (se necessário).
    2. Executa a limpeza do histórico.
    3. Restaura o remote 'origin'.
    4. Solicita confirmação para o push forçado.

    
    OBSERVAÇÃO: Esta operação é destrutiva e reescreve o histórico do commit.
#>

$RepoUrl = "https://github.com/rco-mcti/COIAI.git"

Write-Host "🚧 INICIANDO LIMPEZA DE HISTÓRICO GIT (DOCX/PDF) 🚧" -ForegroundColor Yellow
Write-Host "ATENÇÃO: Este processo reescreve todo o histórico do Git!" -ForegroundColor Red

# 1. Instalação do git-filter-repo
Write-Host "`n📦 Verificando/Instalando git-filter-repo..." -ForegroundColor Cyan
try {
    pip install git-filter-repo
} catch {
    Write-Error "Falha ao instalar git-filter-repo via pip. Verifique se o Python está instalado/no PATH."
    exit 1
}

# Confirmação antes de prosseguir com a alteração destrutiva
$confirmation = Read-Host "`nDeseja prosseguir com a remoção de TODOS os .docx e .pdf do histórico? (S/N)"
if ($confirmation -ne 'S' -and $confirmation -ne 's') {
    Write-Host "Operação cancelada."
    exit 0
}

# 2. Execução do git-filter-repo
# --path-glob '*.docx' --path-glob '*.pdf' --invert-paths -> Remove arquivos que batem com esses padrões
Write-Host "`n🧹 Executando git-filter-repo..." -ForegroundColor Cyan
git filter-repo --path-glob '*.docx' --path-glob '*.pdf' --invert-paths --force

# 3. Restauração do remote
Write-Host "`n🔗 Restaurando remote 'origin'..." -ForegroundColor Cyan
git remote add origin $RepoUrl

# 4. Instruções Finais
Write-Host "`n✅ Limpeza local concluída!" -ForegroundColor Green
Write-Host "`n📢 PARA FINALIZAR, EXECUTE OS COMANDOS ABAIXO MANUALMENTE:" -ForegroundColor Yellow
Write-Host "   (Isso enviará o novo histórico para o GitHub, sobrescrevendo o antigo)"
Write-Host "`n   git push origin --force --all"
Write-Host "   git push origin --force --tags"
Write-Host "`n⚠️  Colaboradores precisarão clonar o repositório novamente." -ForegroundColor Red
