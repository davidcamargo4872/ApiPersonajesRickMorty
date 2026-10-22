# API Personajes - Rick y Morty (Blazor WebAssembly)

Aplicacion web hecha con **Blazor WebAssembly** (cliente) y **ASP.NET Core** (servidor) que muestra
la lista de personajes de la API https://rickandmortyapi.com/ con paginacion.

## Como esta organizado

| Proyecto | Que hace |
|----------|----------|
| `ApiPersonajesRickMorty.Client` | Blazor WebAssembly. Es la pantalla que corre en el navegador (`Pages/Index.razor`). |
| `ApiPersonajesRickMorty.Server` | ASP.NET Core. Sirve el cliente y tiene el controlador `api/personajes` que llama a la API de Rick and Morty. |
| `ApiPersonajesRickMorty.Shared` | Clases (modelos) que usan los dos: `Character`, `Origin`, `Location`, `Characters`, `Info`. |

Flujo: navegador -> `GET api/personajes?page=1` (nuestro servidor) -> `GET https://rickandmortyapi.com/api/character?page=1` -> JSON -> pantalla.

## Como ejecutarlo

Requisitos: Visual Studio 2022/2026 con la carga de trabajo "ASP.NET y desarrollo web" y el SDK de .NET 10
(o el que tengas instalado, mira la nota de abajo).

1. Abrir `ApiPersonajesRickMorty.sln`.
2. Clic derecho en `ApiPersonajesRickMorty.Server` > **Establecer como proyecto de inicio**.
3. Presionar **F5**. Se abre el navegador con la lista de personajes.

Por consola:

```
dotnet run --project ApiPersonajesRickMorty.Server
```

Y abrir la direccion que muestre (por defecto https://localhost:7100).

> Nota: los proyectos usan `net10.0`. Si tienes otro SDK (por ejemplo .NET 8), cambia
> `<TargetFramework>` en los 3 `.csproj` y la version `10.0.*` de los paquetes `Microsoft.AspNetCore.Components.WebAssembly*`.
> Con `dotnet --list-sdks` puedes ver cual tienes.

## Probar solo la API del servidor

Con el proyecto corriendo, abrir en el navegador: `https://localhost:7100/api/personajes?page=2`

## Subir a GitHub

```
git init
git add .
git commit -m "Primera version de la app de Rick y Morty"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ApiPersonajesRickMorty.git
git push -u origin main
```
