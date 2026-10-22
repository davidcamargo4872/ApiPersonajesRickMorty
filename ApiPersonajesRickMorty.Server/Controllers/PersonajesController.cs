using ApiPersonajesRickMorty.Shared.Models;
using Microsoft.AspNetCore.Mvc;

namespace ApiPersonajesRickMorty.Server.Controllers
{
    [ApiController]
    [Route("api/[controller]")]   // como se llama PersonajesController, la ruta queda api/personajes
    public class PersonajesController : ControllerBase
    {
        private readonly HttpClient _http;

        public PersonajesController(IHttpClientFactory fabrica)
        {
            // Usamos el cliente "RickAndMorty" que configuramos en Program.cs
            _http = fabrica.CreateClient("RickAndMorty");
        }

        // GET api/personajes?page=1
        [HttpGet]
        public async Task<ActionResult<Characters>> Get([FromQuery] int page = 1)
        {
            if (page < 1)
            {
                page = 1;
            }

            try
            {
                // Pedimos la pagina a la API externa
                var respuesta = await _http.GetAsync($"character?page={page}");

                if (!respuesta.IsSuccessStatusCode)
                {
                    return StatusCode((int)respuesta.StatusCode,
                        "La API de Rick and Morty no devolvio datos para esa pagina.");
                }

                // Convertimos el JSON a nuestras clases
                var datos = await respuesta.Content.ReadFromJsonAsync<Characters>();
                return Ok(datos);
            }
            catch (HttpRequestException)
            {
                return StatusCode(502, "No se pudo conectar con la API de Rick and Morty.");
            }
        }
    }
}
