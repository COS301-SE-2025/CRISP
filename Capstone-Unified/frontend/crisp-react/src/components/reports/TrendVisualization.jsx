import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const TrendVisualization = ({ temporalTrends, title = "Threat Trends", width, height }) => {
  const svgRef = useRef();
  const containerRef = useRef();

  useEffect(() => {
    if (!temporalTrends || temporalTrends.length === 0) return;

    // Clear previous chart
    d3.select(svgRef.current).selectAll("*").remove();

    // Get responsive dimensions
    const container = containerRef.current;
    const containerWidth = width || (container ? container.offsetWidth : 800);
    const containerHeight = height || 400;

    // Set up dimensions and margins
    const margin = { top: 20, right: 80, bottom: 40, left: 50 };
    const innerWidth = containerWidth - margin.left - margin.right;
    const innerHeight = containerHeight - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("width", containerWidth)
      .attr("height", containerHeight);

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Parse dates and prepare data
    const parseDate = d3.timeParse("%Y-%m-%d");
    const data = temporalTrends.map(d => ({
      date: parseDate(d.date),
      indicators: +d.indicators,
      ttps: +d.ttps,
      totalEvents: +d.total_events
    })).filter(d => d.date !== null);

    if (data.length === 0) return;

    // Set up scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => Math.max(d.indicators, d.ttps, d.totalEvents))])
      .nice()
      .range([innerHeight, 0]);

    // Color scale
    const colorScale = d3.scaleOrdinal()
      .domain(['indicators', 'ttps', 'totalEvents'])
      .range(['#ff6b6b', '#4ecdc4', '#45b7d1']);

    // Create line generator
    const line = d3.line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    // Prepare data for multiple lines
    const seriesData = [
      {
        key: 'indicators',
        name: 'IoC Indicators',
        values: data.map(d => ({ date: d.date, value: d.indicators })),
        color: '#ff6b6b'
      },
      {
        key: 'ttps',
        name: 'TTPs',
        values: data.map(d => ({ date: d.date, value: d.ttps })),
        color: '#4ecdc4'
      },
      {
        key: 'totalEvents',
        name: 'Total Events',
        values: data.map(d => ({ date: d.date, value: d.totalEvents })),
        color: '#45b7d1'
      }
    ];

    // Add X axis
    g.append("g")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale)
        .tickFormat(d3.timeFormat("%m/%d"))
        .ticks(Math.min(data.length, 8)))
      .selectAll("text")
      .style("font-size", "12px")
      .style("fill", "#666");

    // Add Y axis
    g.append("g")
      .call(d3.axisLeft(yScale)
        .ticks(6))
      .selectAll("text")
      .style("font-size", "12px")
      .style("fill", "#666");

    // Add axis labels
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (innerHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Count");

    g.append("text")
      .attr("transform", `translate(${innerWidth / 2}, ${innerHeight + margin.bottom})`)
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text("Date");

    // Add title
    g.append("text")
      .attr("x", innerWidth / 2)
      .attr("y", 0 - (margin.top / 2))
      .attr("text-anchor", "middle")
      .style("font-size", "16px")
      .style("font-weight", "600")
      .style("fill", "#333")
      .text(title);

    // Create tooltip
    const tooltip = d3.select("body").append("div")
      .attr("class", "d3-tooltip")
      .style("opacity", 0)
      .style("position", "absolute")
      .style("background", "rgba(0, 0, 0, 0.8)")
      .style("color", "white")
      .style("padding", "8px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("z-index", "1000");

    // Add lines
    const series = g.selectAll(".series")
      .data(seriesData)
      .enter().append("g")
      .attr("class", "series");

    series.append("path")
      .attr("class", "line")
      .attr("d", d => line(d.values))
      .style("fill", "none")
      .style("stroke", d => d.color)
      .style("stroke-width", 2.5)
      .style("opacity", 0.8);

    // Add dots for data points
    series.selectAll(".dot")
      .data(d => d.values.map(v => ({ ...v, key: d.key, name: d.name, color: d.color })))
      .enter().append("circle")
      .attr("class", "dot")
      .attr("cx", d => xScale(d.date))
      .attr("cy", d => yScale(d.value))
      .attr("r", 4)
      .style("fill", d => d.color)
      .style("stroke", "white")
      .style("stroke-width", 2)
      .style("cursor", "pointer")
      .on("mouseover", function(event, d) {
        tooltip.transition()
          .duration(200)
          .style("opacity", .9);
        tooltip.html(`
          <strong>${d.name}</strong><br/>
          Date: ${d3.timeFormat("%Y-%m-%d")(d.date)}<br/>
          Count: ${d.value}
        `)
          .style("left", (event.pageX + 10) + "px")
          .style("top", (event.pageY - 28) + "px");
        
        d3.select(this)
          .transition()
          .duration(100)
          .attr("r", 6);
      })
      .on("mouseout", function(d) {
        tooltip.transition()
          .duration(500)
          .style("opacity", 0);
        
        d3.select(this)
          .transition()
          .duration(100)
          .attr("r", 4);
      });

    // Add legend
    const legend = g.append("g")
      .attr("class", "legend")
      .attr("transform", `translate(${innerWidth - 120}, 20)`);

    const legendItems = legend.selectAll(".legend-item")
      .data(seriesData)
      .enter().append("g")
      .attr("class", "legend-item")
      .attr("transform", (d, i) => `translate(0, ${i * 20})`);

    legendItems.append("line")
      .attr("x1", 0)
      .attr("x2", 15)
      .attr("y1", 0)
      .attr("y2", 0)
      .style("stroke", d => d.color)
      .style("stroke-width", 3);

    legendItems.append("text")
      .attr("x", 20)
      .attr("y", 0)
      .attr("dy", "0.35em")
      .style("font-size", "12px")
      .style("fill", "#666")
      .text(d => d.name);

    // Add grid lines
    g.append("g")
      .attr("class", "grid")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(d3.axisBottom(xScale)
        .tickSize(-innerHeight)
        .tickFormat("")
      )
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

    g.append("g")
      .attr("class", "grid")
      .call(d3.axisLeft(yScale)
        .tickSize(-innerWidth)
        .tickFormat("")
      )
      .style("stroke-dasharray", "3,3")
      .style("opacity", 0.3);

    // Cleanup function
    return () => {
      tooltip.remove();
    };

  }, [temporalTrends, title, width, height]);

  return (
    <div ref={containerRef} className="trend-visualization" style={{ width: '100%', overflowX: 'auto' }}>
      <svg ref={svgRef}></svg>
      <style>{`
        .trend-visualization {
          background: white;
          border-radius: 8px;
          padding: 16px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin: 16px 0;
        }
        
        .trend-visualization svg {
          display: block;
          margin: 0 auto;
        }
        
        :global(.d3-tooltip) {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        :global(.grid line) {
          stroke: #ddd;
        }
        
        :global(.grid path) {
          stroke-width: 0;
        }
        
        .trend-visualization :global(.domain) {
          stroke: #ccc;
        }
        
        .trend-visualization :global(.tick line) {
          stroke: #ccc;
        }
      `}</style>
    </div>
  );
};

export default TrendVisualization;