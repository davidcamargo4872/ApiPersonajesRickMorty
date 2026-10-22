var builder = WebApplication.CreateBuilder(args);

// Activamos los controladores (MVC) para poder tener api/personajes
builder.Services.AddControllers();

// HttpClient con nombre para llamar a la API de Rick and Morty
builder.Services.AddHttpClient("RickAndMorty", cliente =>
{
    cliente.BaseAddress = new Uri("https://rickandmortyapi.com/api/");
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseWebAssemblyDebugging();
}
else
{
    app.UseHsts();
}

app.UseHttpsRedirection();

// Sirve los archivos del cliente Blazor WebAssembly (_framework, etc.)
app.UseBlazorFrameworkFiles();
app.UseStaticFiles();

app.UseRouting();

app.MapControllers();

// Cualquier ruta que no sea de la API devuelve el index.html del cliente
app.MapFallbackToFile("index.html");

app.Run();
