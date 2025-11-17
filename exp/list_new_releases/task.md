This request searches for new album releases on Spotify using the `tag:new` filter.
curl --request GET \
  --url 'https://api.spotify.com/v1/search?q=tag%3Anew&type=album&limit=2&offset=0' \
  --header 'Authorization: Bearer 1POdFZRZbvb...qqillRxMr2z'

This is spotify response for the above request:
```json
{
  "albums": {
    "href": "https://api.spotify.com/v1/search?offset=0&limit=2&query=tag%3Anew&type=album&locale=en-US,en;q%3D0.9,ru;q%3D0.8,th;q%3D0.7,zh-TW;q%3D0.6,zh;q%3D0.5,ja;q%3D0.4,es;q%3D0.3",
    "limit": 2,
    "next": "https://api.spotify.com/v1/search?offset=2&limit=2&query=tag%3Anew&type=album&locale=en-US,en;q%3D0.9,ru;q%3D0.8,th;q%3D0.7,zh-TW;q%3D0.6,zh;q%3D0.5,ja;q%3D0.4,es;q%3D0.3",
    "offset": 0,
    "previous": null,
    "total": 100,
    "items": [
      {
        "album_type": "album",
        "total_tracks": 24,
        "available_markets": [
          "AE",
          "AM",
          "AU",
          "AZ",
          "BD",
          "BG",
          "BH",
          "BI",
          "BN",
          "BT",
          "BW",
          "BY",
          "CY",
          "DJ",
          "EE",
          "EG",
          "ET",
          "FI",
          "FJ",
          "FM",
          "GE",
          "GR",
          "HK",
          "ID",
          "IL",
          "IN",
          "IQ",
          "JO",
          "JP",
          "KE",
          "KG",
          "KH",
          "KI",
          "KM",
          "KR",
          "KW",
          "KZ",
          "LA",
          "LB",
          "LK",
          "LS",
          "LT",
          "LV",
          "LY",
          "MD",
          "MG",
          "MH",
          "MN",
          "MO",
          "MU",
          "MV",
          "MW",
          "MY",
          "MZ",
          "NA",
          "NP",
          "NR",
          "NZ",
          "OM",
          "PG",
          "PH",
          "PK",
          "PS",
          "PW",
          "QA",
          "RO",
          "RW",
          "SA",
          "SB",
          "SC",
          "SG",
          "SZ",
          "TH",
          "TJ",
          "TL",
          "TO",
          "TR",
          "TV",
          "TW",
          "TZ",
          "UA",
          "UG",
          "UZ",
          "VN",
          "VU",
          "WS",
          "ZA",
          "ZM",
          "ZW",
          "AD",
          "AL",
          "AO",
          "AT",
          "BA",
          "BE",
          "BJ",
          "CD",
          "CG",
          "CH",
          "CM",
          "CZ",
          "DE",
          "DK",
          "DZ",
          "ES",
          "FR",
          "GA",
          "GQ",
          "HR",
          "HU",
          "IT",
          "LI",
          "LU",
          "MA",
          "MC",
          "ME",
          "MK",
          "MT",
          "NE",
          "NG",
          "NL",
          "NO",
          "PL",
          "RS",
          "SE",
          "SI",
          "SK",
          "SM",
          "TD",
          "TN",
          "XK",
          "BF",
          "CI",
          "GB",
          "GH",
          "GM",
          "GN",
          "GW",
          "IE",
          "IS",
          "LR",
          "ML",
          "MR",
          "PT",
          "SL",
          "SN",
          "ST",
          "TG",
          "CV",
          "AR",
          "BR",
          "CL",
          "PY",
          "SR",
          "UY",
          "AG",
          "BB",
          "BO",
          "CW",
          "DM",
          "DO",
          "GD",
          "GY",
          "KN",
          "LC",
          "PR",
          "TT",
          "VC",
          "VE",
          "BS",
          "CA",
          "CO",
          "EC",
          "HT",
          "JM",
          "PA",
          "PE",
          "US",
          "BZ",
          "CR",
          "GT",
          "HN",
          "MX",
          "NI",
          "SV"
        ],
        "external_urls": {
          "spotify": "https://open.spotify.com/album/75984q4OpwTLsczbfazWaI"
        },
        "href": "https://api.spotify.com/v1/albums/75984q4OpwTLsczbfazWaI",
        "id": "75984q4OpwTLsczbfazWaI",
        "images": [
          {
            "height": 640,
            "url": "https://i.scdn.co/image/ab67616d0000b273e84889d701a64a1e2dceef75",
            "width": 640
          },
          {
            "height": 300,
            "url": "https://i.scdn.co/image/ab67616d00001e02e84889d701a64a1e2dceef75",
            "width": 300
          },
          {
            "height": 64,
            "url": "https://i.scdn.co/image/ab67616d00004851e84889d701a64a1e2dceef75",
            "width": 64
          }
        ],
        "name": "Miligram Hits Live",
        "release_date": "2025-11-11",
        "release_date_precision": "day",
        "type": "album",
        "uri": "spotify:album:75984q4OpwTLsczbfazWaI",
        "artists": [
          {
            "external_urls": {
              "spotify": "https://open.spotify.com/artist/3uV7fmwEFZqp3mp2gTDB5s"
            },
            "href": "https://api.spotify.com/v1/artists/3uV7fmwEFZqp3mp2gTDB5s",
            "id": "3uV7fmwEFZqp3mp2gTDB5s",
            "name": "Ceca",
            "type": "artist",
            "uri": "spotify:artist:3uV7fmwEFZqp3mp2gTDB5s"
          }
        ]
      },
      {
        "album_type": "single",
        "total_tracks": 1,
        "available_markets": [
          "AD",
          "AE",
          "AG",
          "AL",
          "AM",
          "AO",
          "AR",
          "AT",
          "AU",
          "AZ",
          "BA",
          "BB",
          "BD",
          "BE",
          "BF",
          "BG",
          "BH",
          "BI",
          "BJ",
          "BN",
          "BO",
          "BR",
          "BS",
          "BT",
          "BW",
          "BZ",
          "CA",
          "CD",
          "CG",
          "CH",
          "CI",
          "CL",
          "CM",
          "CO",
          "CR",
          "CV",
          "CW",
          "CY",
          "CZ",
          "DE",
          "DJ",
          "DK",
          "DM",
          "DO",
          "DZ",
          "EC",
          "EE",
          "EG",
          "ES",
          "ET",
          "FI",
          "FJ",
          "FM",
          "FR",
          "GA",
          "GB",
          "GD",
          "GE",
          "GH",
          "GM",
          "GN",
          "GQ",
          "GR",
          "GT",
          "GW",
          "GY",
          "HK",
          "HN",
          "HR",
          "HT",
          "HU",
          "ID",
          "IE",
          "IL",
          "IN",
          "IQ",
          "IS",
          "IT",
          "JM",
          "JO",
          "JP",
          "KE",
          "KG",
          "KH",
          "KI",
          "KM",
          "KN",
          "KR",
          "KW",
          "KZ",
          "LA",
          "LB",
          "LC",
          "LI",
          "LK",
          "LR",
          "LS",
          "LT",
          "LU",
          "LV",
          "LY",
          "MA",
          "MC",
          "MD",
          "ME",
          "MG",
          "MH",
          "MK",
          "ML",
          "MN",
          "MO",
          "MR",
          "MT",
          "MU",
          "MV",
          "MW",
          "MX",
          "MY",
          "MZ",
          "NA",
          "NE",
          "NG",
          "NI",
          "NL",
          "NO",
          "NP",
          "NR",
          "NZ",
          "OM",
          "PA",
          "PE",
          "PG",
          "PH",
          "PK",
          "PL",
          "PS",
          "PT",
          "PW",
          "PY",
          "QA",
          "RO",
          "RS",
          "RW",
          "SA",
          "SB",
          "SC",
          "SE",
          "SG",
          "SI",
          "SK",
          "SL",
          "SM",
          "SN",
          "SR",
          "ST",
          "SV",
          "SZ",
          "TD",
          "TG",
          "TH",
          "TJ",
          "TL",
          "TN",
          "TO",
          "TR",
          "TT",
          "TV",
          "TW",
          "TZ",
          "UA",
          "UG",
          "US",
          "UY",
          "UZ",
          "VC",
          "VE",
          "VN",
          "VU",
          "WS",
          "XK",
          "ZA",
          "ZM",
          "ZW"
        ],
        "external_urls": {
          "spotify": "https://open.spotify.com/album/4w96kbeZiq2Q2n8dDAVi4K"
        },
        "href": "https://api.spotify.com/v1/albums/4w96kbeZiq2Q2n8dDAVi4K",
        "id": "4w96kbeZiq2Q2n8dDAVi4K",
        "images": [
          {
            "height": 640,
            "url": "https://i.scdn.co/image/ab67616d0000b27365459c5f28c3d70eb09da9fd",
            "width": 640
          },
          {
            "height": 300,
            "url": "https://i.scdn.co/image/ab67616d00001e0265459c5f28c3d70eb09da9fd",
            "width": 300
          },
          {
            "height": 64,
            "url": "https://i.scdn.co/image/ab67616d0000485165459c5f28c3d70eb09da9fd",
            "width": 64
          }
        ],
        "name": "M.I.A (VALORANT Game Changers Version)",
        "release_date": "2025-11-11",
        "release_date_precision": "day",
        "type": "album",
        "uri": "spotify:album:4w96kbeZiq2Q2n8dDAVi4K",
        "artists": [
          {
            "external_urls": {
              "spotify": "https://open.spotify.com/artist/3c0gDdb9lhnHGFtP4prQpn"
            },
            "href": "https://api.spotify.com/v1/artists/3c0gDdb9lhnHGFtP4prQpn",
            "id": "3c0gDdb9lhnHGFtP4prQpn",
            "name": "KATSEYE",
            "type": "artist",
            "uri": "spotify:artist:3c0gDdb9lhnHGFtP4prQpn"
          },
          {
            "external_urls": {
              "spotify": "https://open.spotify.com/artist/3wrFoI9EVjWg6m8xXeWr5t"
            },
            "href": "https://api.spotify.com/v1/artists/3wrFoI9EVjWg6m8xXeWr5t",
            "id": "3wrFoI9EVjWg6m8xXeWr5t",
            "name": "VALORANT",
            "type": "artist",
            "uri": "spotify:artist:3wrFoI9EVjWg6m8xXeWr5t"
          }
        ]
      }
    ]
  }
}
```


Text of the spotify API documentation for this endpoint:
```text
Request

GET
/search
q
string
Required
Your search query.

You can narrow down your search using field filters. The available filters are album, artist, track, year, upc, tag:hipster, tag:new, isrc, and genre. Each field filter only applies to certain result types.

The artist and year filters can be used while searching albums, artists and tracks. You can filter on a single year or a range (e.g. 1955-1960).
The album filter can be used while searching albums and tracks.
The genre filter can be used while searching artists and tracks.
The isrc and track filters can be used while searching tracks.
The upc, tag:new and tag:hipster filters can only be used while searching albums. The tag:new filter will return albums released in the past two weeks and tag:hipster can be used to return only albums with the lowest 10% popularity.

Example: q=remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis
type
array of strings
Required
A comma-separated list of item types to search across. Search results include hits from all the specified item types. For example: q=abacab&type=album,track returns both albums and tracks matching "abacab".

Allowed values: "album", "artist", "playlist", "track", "show", "episode", "audiobook"
market
string
An ISO 3166-1 alpha-2 country code. If a country code is specified, only content that is available in that market will be returned.
If a valid user access token is specified in the request header, the country associated with the user account will take priority over this parameter.
Note: If neither market or user country are provided, the content is considered unavailable for the client.
Users can view the country that is associated with their account in the account settings.

Example: market=ES
limit
integer
The maximum number of results to return in each item type.

Default: limit=20
Range: 0 - 50
Example: limit=10
offset
integer
The index of the first result to return. Use with limit to get the next page of search results.

Default: offset=0
Range: 0 - 1000
Example: offset=5
include_external
string
If include_external=audio is specified it signals that the client can play externally hosted audio content, and marks the content as playable in the response. By default externally hosted audio content is marked as unplayable in the response.

Allowed values: "audio"
Response
200
401
403
429
Search response


tracks
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of TrackObject
Required

artists
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of ArtistObject
Required

albums
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of SimplifiedAlbumObject
Required
album_type
string
Required
The type of the album.

Allowed values: "album", "single", "compilation"
Example: "compilation"
total_tracks
integer
Required
The number of tracks in the album.

Example: 9
available_markets
array of strings
Required
The markets in which the album is available: ISO 3166-1 alpha-2 country codes. NOTE: an album is considered available in a market when at least 1 of its tracks is available in that market.

Example: ["CA","BR","IT"]

external_urls
object
Required
Known external URLs for this album.

href
string
Required
A link to the Web API endpoint providing full details of the album.

id
string
Required
The Spotify ID for the album.

Example: "2up3OPMp9Tb4dAKM2erWXQ"

images
array of ImageObject
Required
The cover art for the album in various sizes, widest first.

name
string
Required
The name of the album. In case of an album takedown, the value may be an empty string.

release_date
string
Required
The date the album was first released.

Example: "1981-12"
release_date_precision
string
Required
The precision with which release_date value is known.

Allowed values: "year", "month", "day"
Example: "year"

restrictions
object
Included in the response when a content restriction is applied.

type
string
Required
The object type.

Allowed values: "album"
uri
string
Required
The Spotify URI for the album.

Example: "spotify:album:2up3OPMp9Tb4dAKM2erWXQ"

artists
array of SimplifiedArtistObject
Required
The artists of the album. Each artist object includes a link in href to more detailed information about the artist.


external_urls
object
Known external URLs for this artist.

href
string
A link to the Web API endpoint providing full details of the artist.

id
string
The Spotify ID for the artist.

name
string
The name of the artist.

type
string
The object type.

Allowed values: "artist"
uri
string
The Spotify URI for the artist.


playlists
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of SimplifiedPlaylistObject
Required

shows
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of SimplifiedShowObject
Required

episodes
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of SimplifiedEpisodeObject
Required

audiobooks
object
href
string
Required
A link to the Web API endpoint returning the full result of the request

Example: "https://api.spotify.com/v1/me/shows?offset=0&limit=20"
limit
integer
Required
The maximum number of items in the response (as set in the query or by default).

Example: 20
next
string
Required
Nullable
URL to the next page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
offset
integer
Required
The offset of the items returned (as set in the query or by default)

Example: 0
previous
string
Required
Nullable
URL to the previous page of items. ( null if none)

Example: "https://api.spotify.com/v1/me/shows?offset=1&limit=1"
total
integer
Required
The total number of items available to return.

Example: 4

items
array of SimplifiedAudiobookObject
Required
```

The task
Using information above write a python script that lists all new albums using available params or pagination from the response. I want to have a csv file for each release date from the responses. The csv file should contain: id, name, artists (comma separated), release_date, total_tracks, spotify_url.
The script should read required Spotify API credentials from environment variables SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET and read it from .env file. The script should handle pagination to retrieve all new releases including retries on failures (including 429) with a cooldown logic between retries. the script can use requests  library.