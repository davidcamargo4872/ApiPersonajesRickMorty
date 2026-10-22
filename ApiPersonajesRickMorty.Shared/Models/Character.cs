using System.Text.Json.Serialization;

namespace ApiPersonajesRickMorty.Shared.Models
{
    // Un personaje de la serie, igual a como lo devuelve la API de Rick and Morty
    public class Character
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;

        [JsonPropertyName("species")]
        public string Species { get; set; } = string.Empty;

        [JsonPropertyName("type")]
        public string Type { get; set; } = string.Empty;

        [JsonPropertyName("gender")]
        public string Gender { get; set; } = string.Empty;

        [JsonPropertyName("origin")]
        public Origin Origin { get; set; } = new Origin();

        [JsonPropertyName("location")]
        public Location Location { get; set; } = new Location();

        [JsonPropertyName("image")]
        public string Image { get; set; } = string.Empty;

        // Lista con las URL de los episodios donde aparece
        [JsonPropertyName("episode")]
        public List<string> Episode { get; set; } = new List<string>();

        [JsonPropertyName("url")]
        public string Url { get; set; } = string.Empty;

        [JsonPropertyName("created")]
        public string Created { get; set; } = string.Empty;
    }

    // Planeta o lugar de origen del personaje
    public class Origin
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("url")]
        public string Url { get; set; } = string.Empty;
    }

    // Ultima ubicacion conocida del personaje
    public class Location
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("url")]
        public string Url { get; set; } = string.Empty;
    }
}
