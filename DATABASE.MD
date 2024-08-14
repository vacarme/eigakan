# Query Analysis
⚠️ *outdated since data model has been changed.*


As is table' sizes are:
```shell
                                      List of relations
 Schema |  Name   | Type  |  Owner   | Persistence | Access method |    Size    | Description
--------+---------+-------+----------+-------------+---------------+------------+-------------
 api    | owner   | table | postgres | permanent   | heap          | 16 kB      |
 api    | prog    | table | postgres | permanent   | heap          | 8192 bytes |
 api    | theater | table | postgres | permanent   | heap          | 704 kB     |
(3 rows)
```


## Hypothesis
+ Table `theater` has a (approximately) definitive size and is not expected to grow significantly in the future, no frequent insertions or deletions.
+ table `owner` should be smaller than theater (~same rows numbner and less data), a bit more frequent insertions or deletions.
+ table `prog` can become huge depending on historization policy, lots of insertions and updates/delete.
+ most of the times all query parameters will be used and with an even repartition (if not no-index or partial indexes can come into play).

💡 Indexes are more or less free on `theater` and `owner` tables, but should be used wisely on `prog` table.

## Analysis
Within the current state of the API. Running `EXPLAIN (ANALYSE)`


### Nearest Theater Query
```sql
SELECT api.theater.osm_id, api.theater.ref_cnc, api.theater.name, api.theater.marque, api.theater.wheelchair, api.theater.opening_hours, api.theater.open_air, api.theater.drive_in, api.theater.cinema3d, api.theater.nb_screens, api.theater.capacity, api.theater.acoustic, api.theater.website, api.theater.phone, api.theater.facebook, api.theater.wikidata, api.theater.siret, api.theater.com_insee, api.theater.com_nom, ST_AsEWKB(api.theater.geometry) AS geometry, api.theater.id
FROM api.theater
ORDER BY ST_Distance(api.theater.geometry, ST_GeomFromText('POINT(2.2646354 48.8589384)', 4326)) ASC;
```

#### Recommendations
+ composite index on `wheelchair` and `nb_screens`.

#### Analyse

+ spatial index is not used:

    ```shell
    Sort  (cost=27174.79..27180.13 rows=2135 width=301) (actual time=5.816..5.940 rows=2135 loops=1)
    Sort Key: (st_distance(geometry, '0101000020E610000039E9222AF91D0240A8A388B1F16D4840'::geometry))
    Sort Method: quicksort  Memory: 716kB
    ->  Seq Scan on theater  (cost=0.00..27056.72 rows=2135 width=301) (actual time=0.037..3.866 rows=2135 loops=1)
    Planning Time: 0.225 ms
    Execution Time: 6.276 ms
    ```

    + adding a *gist* index on `geometry`:
    ```shell
    Sort  (cost=27174.79..27180.13 rows=2135 width=301) (actual time=7.233..7.541 rows=2135 loops=1)
        Sort Key: (st_distance(geometry, '0101000020E610000039E9222AF91D0240A8A388B1F16D4840'::geometry))
        Sort Method: quicksort  Memory: 716kB
        ->  Seq Scan on theater  (cost=0.00..27056.72 rows=2135 width=301) (actual time=0.120..4.083 rows=2135 loops=1)
    Planning Time: 0.757 ms
    Execution Time: 8.577 ms
    (6 rows)
    ```

+ fastest conf for this request seems to be a composite index (`wheelchair`, `nb_screens`), the `com_insee` part of the statement is not using the index. 

    + index on wheelchair:
    ```shell

    Sort  (cost=84.31..84.31 rows=1 width=301) (actual time=0.439..0.443 rows=0 loops=1)
    Sort Key: (st_distance(geometry, '0101000020E610000039E9222AF91D0240A8A388B1F16D4840'::geometry))
    Sort Method: quicksort  Memory: 25kB
    ->  Bitmap Heap Scan on theater  (cost=4.56..84.30 rows=1 width=301) (actual time=0.409..0.411 rows=0 loops=1)
        Recheck Cond: (wheelchair = 'limited'::text)
        Filter: ((com_insee ~~ '75%%'::text) AND (nb_screens = 3))
        Rows Removed by Filter: 37
        Heap Blocks: exact=33
        ->  Bitmap Index Scan on idx_wheel  (cost=0.00..4.56 rows=37 width=0) (actual time=0.145..0.146 rows=37 loops=1)
                Index Cond: (wheelchair = 'limited'::text)
    Planning Time: 1.067 ms
    Execution Time: 0.639 ms
    ```

    + adding an index on `com_insee`:
    ```shell
    Sort  (cost=84.31..84.31 rows=1 width=301) (actual time=0.417..0.420 rows=0 loops=1)
    Sort Key: (st_distance(geometry, '0101000020E610000039E9222AF91D0240A8A388B1F16D4840'::geometry))
    Sort Method: quicksort  Memory: 25kB
    ->  Bitmap Heap Scan on theater  (cost=4.56..84.30 rows=1 width=301) (actual time=0.389..0.390 rows=0 loops=1)
        Recheck Cond: (wheelchair = 'limited'::text)
        Filter: ((com_insee ~~ '75%%'::text) AND (nb_screens = 3))
        Rows Removed by Filter: 37
        Heap Blocks: exact=33
        ->  Bitmap Index Scan on idx_wheel  (cost=0.00..4.56 rows=37 width=0) (actual time=0.199..0.200 rows=37 loops=1)
                Index Cond: (wheelchair = 'limited'::text)
    Planning Time: 1.075 ms
    Execution Time: 0.650 ms
    ```

    + adding an index on `nb_screens`:
    ```shell
    after nb_screens
    Sort  (cost=29.69..29.70 rows=1 width=301) (actual time=0.315..0.320 rows=0 loops=1)
    Sort Key: (st_distance(geometry, '0101000020E610000039E9222AF91D0240A8A388B1F16D4840'::geometry))
    Sort Method: quicksort  Memory: 25kB
    ->  Bitmap Heap Scan on theater  (cost=9.97..29.68 rows=1 width=301) (actual time=0.283..0.285 rows=0 loops=1)
        Recheck Cond: ((wheelchair = 'limited'::text) AND (nb_screens = 3))
        Filter: (com_insee ~~ '75%%'::text)
        Rows Removed by Filter: 3
        Heap Blocks: exact=3
        ->  BitmapAnd  (cost=9.97..9.97 rows=2 width=0) (actual time=0.204..0.206 rows=0 loops=1)
                ->  Bitmap Index Scan on idx_wheel  (cost=0.00..4.56 rows=37 width=0) (actual time=0.159..0.159 rows=37 loops=1)
                    Index Cond: (wheelchair = 'limited'::text)
                ->  Bitmap Index Scan on idx_screen  (cost=0.00..5.16 rows=117 width=0) (actual time=0.032..0.032 rows=117 loops=1)
                    Index Cond: (nb_screens = 3)
    Planning Time: 1.133 ms
    Execution Time: 0.520 ms
    ```

    + adding a composite index on `wheelchair` and `nb_screens`:
    ```shell
    Sort  (cost=24.00..24.01 rows=1 width=301) (actual time=0.224..0.228 rows=0 loops=1)
    Sort Key: (st_distance(geometry, '0101000020E610000039E9222AF91D0240A8A388B1F16D4840'::geometry))
    Sort Method: quicksort  Memory: 25kB
    ->  Index Scan using idx_wheel_screen on theater  (cost=0.28..23.99 rows=1 width=301) (actual time=0.194..0.195 rows=0 loops=1)
        Index Cond: ((wheelchair = 'limited'::text) AND (nb_screens = 3))
        Filter: (com_insee ~~ '75%%'::text)
        Rows Removed by Filter: 3
    Planning Time: 0.994 ms
    Execution Time: 0.379 ms
    ```

### Create a Movie Session
```sql
SELECT api.theater.osm_id, api.theater.ref_cnc, api.theater.name, api.theater.marque, api.theater.wheelchair, api.theater.opening_hours, api.theater.open_air, api.theater.drive_in, api.theater.cinema3d, api.theater.nb_screens, api.theater.capacity, api.theater.acoustic, api.theater.website, api.theater.phone, api.theater.facebook, api.theater.wikidata, api.theater.siret, api.theater.com_insee, api.theater.com_nom, ST_AsEWKB(api.theater.geometry) AS geometry, api.theater.id
FROM api.theater, api.owner
WHERE api.theater.id = '20e4a4c1-74a9-4fbd-a088-4220a5c709f8' AND api.owner.siret = api.theater.siret;
```
+ no index needed as the query is on the primary key of the table.

```shell
 Hash Join  (cost=8.31..31.94 rows=1 width=293) (actual time=0.399..0.432 rows=1 loops=1)
   Hash Cond: (owner.siret = theater.siret)
   ->  Seq Scan on owner  (cost=0.00..20.70 rows=1070 width=32) (actual time=0.070..0.082 rows=1 loops=1)
   ->  Hash  (cost=8.30..8.30 rows=1 width=404) (actual time=0.137..0.142 rows=1 loops=1)
         Buckets: 1024  Batches: 1  Memory Usage: 9kB
         ->  Index Scan using theater_pkey on theater  (cost=0.28..8.30 rows=1 width=404) (actual time=0.105..0.113 rows=1 loops=1)
               Index Cond: (id = '20e4a4c1-74a9-4fbd-a088-4220a5c709f8'::uuid)
 Planning Time: 1.112 ms
 Execution Time: 0.647 ms
```