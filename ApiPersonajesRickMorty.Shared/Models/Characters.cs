using System.Text.Json.Serialization;

namespace ApiPersonajesRickMorty.Shared.Models
{
    // Es la respuesta completa de la API: la parte "info" y la lista "results"
    public class Characters
    {
        [JsonPropertyName("info")]
        public Info Info { get; set; } = new Info();

        [JsonPropertyName("results")]
        public List<Character> Results { get; set; } = new List<Character>();
    }

    // Datos de la paginacion
    public class Info
    {
        [JsonPropertyName("count")]
        public int Count { get; set; }

        [JsonPropertyName("pages")]
        public int Pages { get; set; }

        // Pueden ser null (por ejemplo, en la pagina 1 no hay "prev"), por eso string?
        [JsonPropertyName("next")]
        public string? Next { get; set; }

        [JsonPropertyName("prev")]
        public string? Prev { get; set; }
    }
}
