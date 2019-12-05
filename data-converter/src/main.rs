//! Quick and dirty tool for changing data formats to CSVs

use std::io::{BufRead, BufReader};
use std::sync::Mutex;

use clap::clap_app;

use csv::WriterBuilder;

use itertools::Itertools;

use rayon::prelude::*;

use regex::Regex;

use serde::Serialize;

enum Formats {
    TimeMmapTouch, // Timestamp
    TimeElapsed,   // Timestamp
    Locality,      // Latency per op
    ThpOps,        // Units are ops per page
    Memcached,     // Latency per 100 reqs
    BuddyInfo,     // Chunks in each buddy list order
}

/// Validate that string is a valid filename
fn file_exists(filename: String) -> Result<(), String> {
    let meta = std::fs::metadata(&filename).map_err(|e| format!("{}", e))?;
    if meta.is_file() {
        Ok(())
    } else {
        Err(format!("Not a regular file: {}", filename))
    }
}

fn main() {
    let matches = clap_app! {muncher =>
        (about: "Munches data")
        (@arg FILENAME: +required +takes_value {file_exists})
        (@arg OUTFILENAME: +required +takes_value)
        (@group WHICH =>
            (@attributes +required)
            (@arg TIMEMMAPTOUCH: --time_mmap_touch)
            (@arg TIMEELAPSED: --time_elapsed)
            (@arg LOCALITY: --locality)
            (@arg THPOPS: --thp_ops_per_page)
            (@arg MEMCACHED: --memcached)
            (@arg BUDDYINFO: --buddyinfo)
        )
    }
    .get_matches();

    let infilename = matches.value_of("FILENAME").unwrap();
    let outfilename = matches.value_of("OUTFILENAME").unwrap();

    let which = if matches.is_present("TIMEMMAPTOUCH") {
        Formats::TimeMmapTouch
    } else if matches.is_present("TIMEELAPSED") {
        Formats::TimeElapsed
    } else if matches.is_present("LOCALITY") {
        Formats::Locality
    } else if matches.is_present("THPOPS") {
        Formats::ThpOps
    } else if matches.is_present("MEMCACHED") {
        Formats::Memcached
    } else if matches.is_present("BUDDYINFO") {
        Formats::BuddyInfo
    } else {
        unreachable!();
    };

    dispatch(which, infilename, outfilename);
}

fn dispatch(which: Formats, infilename: &str, outfilename: &str) {
    match which {
        Formats::TimeMmapTouch => convert_single_int::<TimestampRow>(2, infilename, outfilename),
        Formats::TimeElapsed => convert_single_int::<TimestampRow>(0, infilename, outfilename),
        Formats::Locality => convert_single_int::<LatencyPerOpRow>(0, infilename, outfilename),
        Formats::ThpOps => convert_single_int::<OpsPerPageRow>(0, infilename, outfilename),
        Formats::Memcached => convert_memcached(infilename, outfilename),
        Formats::BuddyInfo => convert_buddyinfo(infilename, outfilename),
    };
}

fn convert_single_int<R: SingleIntRow>(skip: usize, infilename: &str, outfilename: &str) {
    let infile = std::fs::File::open(infilename).expect("unable to open input file");
    let reader = BufReader::new(infile);
    let writer = Mutex::new(
        WriterBuilder::new()
            .from_path(outfilename)
            .expect("unable to open output file"),
    );

    const SINGLEINT_REGEX: &str = r"^(\d+)$";
    let regex = Regex::new(SINGLEINT_REGEX).expect("regex parsing error");

    reader
        .lines()
        .map(|line| line.expect("unable to read line"))
        .skip(skip)
        .par_bridge()
        .map(|line| process_single_int_line::<R>(&regex, line))
        .for_each(|row| {
            writer
                .lock()
                .unwrap()
                .serialize(row)
                .expect("unable to serialize row")
        });
}

trait SingleIntRow: Send + Serialize {
    fn new(val: usize) -> Self;
}

fn process_single_int_line<Row: SingleIntRow>(regex: &Regex, line: String) -> impl SingleIntRow {
    let captures = regex.captures(&line).expect("expected captures");

    let val = captures
        .get(1)
        .expect("expected capture group 1")
        .as_str()
        .parse()
        .expect("failed to parse capture");

    Row::new(val)
}

fn convert_memcached(infilename: &str, outfilename: &str) {
    let infile = std::fs::File::open(infilename).expect("unable to open input file");
    let reader = BufReader::new(infile);
    let writer = Mutex::new(
        WriterBuilder::new()
            .from_path(outfilename)
            .expect("unable to open output file"),
    );

    const MEMCACHED_REGEX: &str = r"^DONE (\d+) Duration \{ secs: (\d+), nanos: (\d+) \} 0$";
    let regex = Regex::new(MEMCACHED_REGEX).expect("regex parsing error");

    reader
        .lines()
        .map(|line| line.expect("unable to read line"))
        .par_bridge()
        .map(|line| {
            let captures = regex.captures(&line).expect("expected captures");

            let ops = captures
                .get(1)
                .expect("expected capture group 1")
                .as_str()
                .parse()
                .expect("failed to parse capture");

            let secs: usize = captures
                .get(2)
                .expect("expected capture group 2")
                .as_str()
                .parse()
                .expect("failed to parse capture");

            let nanos: usize = captures
                .get(3)
                .expect("expected capture group 2")
                .as_str()
                .parse()
                .expect("failed to parse capture");

            let latency = secs * 1_000_000_000 + nanos;

            MemcachedRow { ops, latency }
        })
        .for_each(|row| {
            writer
                .lock()
                .unwrap()
                .serialize(row)
                .expect("unable to serialize row")
        });
}

fn convert_buddyinfo(infilename: &str, outfilename: &str) {
    let infile = std::fs::File::open(infilename).expect("unable to open input file");
    let reader = BufReader::new(infile);
    let mut writer = WriterBuilder::new()
        .from_path(outfilename)
        .expect("unable to open output file");

    const BUDDYINFO_REGEX: &str = r"^Node\s+\d+,\s+zone\s+(DMA|DMA32|Normal)((\s+\d+)+)\s+$";
    //const BUDDYINFO_REGEX: &str = r"^Node\s+\d+,\s+zone\s+(DMA|DMA32|Normal)(\s+(\d+))+$";
    let regex = Regex::new(BUDDYINFO_REGEX).expect("regex parsing error");

    reader
        .lines()
        .map(|line| line.expect("unable to read line"))
        .chunks(3)
        .into_iter()
        .map(|chunk| process_chunk_buddyinfo(&regex, chunk))
        .for_each(|row| writer.serialize(row).expect("unable to serialize row"));
}

fn process_chunk_buddyinfo(regex: &Regex, chunk: impl Iterator<Item = String>) -> BuddyInfoRow {
    let mut bi = BuddyInfoRow {
        o00: 0,
        o01: 0,
        o02: 0,
        o03: 0,
        o04: 0,
        o05: 0,
        o06: 0,
        o07: 0,
        o08: 0,
        o09: 0,
        o10: 0,
    };

    for line in chunk {
        let captures = regex
            .captures(&line)
            .expect("unable to parse buddyinfo line");

        let orders: Vec<_> = captures
            .get(2)
            .expect("expected capture group")
            .as_str()
            .split_whitespace()
            .map(|v| v.parse::<usize>().unwrap())
            .collect();

        bi.o00 += orders[0] << 0;
        bi.o01 += orders[1] << 1;
        bi.o02 += orders[2] << 2;
        bi.o03 += orders[3] << 0;
        bi.o04 += orders[4] << 0;
        bi.o05 += orders[5] << 0;
        bi.o06 += orders[6] << 0;
        bi.o07 += orders[7] << 0;
        bi.o08 += orders[8] << 0;
        bi.o09 += orders[9] << 0;
        bi.o10 += orders[10] << 10;
    }

    bi
}

///////////////////////////////////////////////////////////////////////////////

#[derive(Serialize)]
struct TimestampRow {
    timestamp: usize,
}

impl SingleIntRow for TimestampRow {
    fn new(timestamp: usize) -> Self {
        Self { timestamp }
    }
}

#[derive(Serialize)]
struct LatencyPerOpRow {
    #[serde(rename = "Latency Per Op")]
    latency: usize,
}

impl SingleIntRow for LatencyPerOpRow {
    fn new(latency: usize) -> Self {
        Self { latency }
    }
}

#[derive(Serialize)]
struct OpsPerPageRow {
    #[serde(rename = "Ops per Page")]
    ops: usize,
}

impl SingleIntRow for OpsPerPageRow {
    fn new(ops: usize) -> Self {
        Self { ops }
    }
}

#[derive(Serialize)]
struct MemcachedRow {
    #[serde(rename = "Number of Insertions Completed")]
    ops: usize,
    #[serde(rename = "Latency of last 100 Insertions (ns)")]
    latency: usize,
}

#[derive(Serialize)]
struct BuddyInfoRow {
    #[serde(rename = "Order 0 Pages")]
    o00: usize,
    #[serde(rename = "Order 1 Pages")]
    o01: usize,
    #[serde(rename = "Order 2 Pages")]
    o02: usize,
    #[serde(rename = "Order 3 Pages")]
    o03: usize,
    #[serde(rename = "Order 4 Pages")]
    o04: usize,
    #[serde(rename = "Order 5 Pages")]
    o05: usize,
    #[serde(rename = "Order 6 Pages")]
    o06: usize,
    #[serde(rename = "Order 7 Pages")]
    o07: usize,
    #[serde(rename = "Order 8 Pages")]
    o08: usize,
    #[serde(rename = "Order 9 Pages")]
    o09: usize,
    #[serde(rename = "Order 10 Pages")]
    o10: usize,
}
