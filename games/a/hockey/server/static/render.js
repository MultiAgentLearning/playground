var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');

var kScale = 3;
var kTeamColors = ["coral", "cornflowerblue"];
var kLidarCategoryColors = ["darkseagreen", "darkred", "darksalmon", "darkolivegreen", "darkorange", "darkmagenta", "darkgoldenrod", "crimson"];
var kTextStartPosition = 100;
var kDataStartPosition = kTextStartPosition + 120;


backoff = 1000;
function getData() {
    $.ajax({
        url: "http://"+location.hostname+":5000/read",
        type:"GET"
    }).done(function(data) {
        backoff = 1000;
        showData(data);
    }).fail(function(data) {
        var start = new Date().getTime();
        var end = start;
        while(end < start + backoff) {
            end = new Date().getTime();
        }
        backoff = Math.min(backoff*2, 4000);
        showData(data);
    });
}
getData();

async function showData(data) {
    context.clearRect(0, 0, canvas.width, canvas.height);

    var players = data.players;
    var board = data.board;
    var time = data.timestep;
    var step = data.stepcount;
    var score = data.score;
    var scored = data.scored;
    var done = data.done;

    if (!players || !board) {
        return;
    }

    drawBoard(board);
    drawPlayers(players);
    drawText(time, score, scored);

    if (done || scored) {
        await sleep(1500);
    }

    getData();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function drawLine(x1, y1, x2, y2, color, lineWidth) {
    context.save()
    context.strokeStyle = color;
    context.beginPath();
    context.moveTo(x1, y1);
    context.lineTo(x2, y2);
    context.lineWidth = lineWidth;
    context.stroke();
    context.restore();
}

function drawCircle(x1, y1, radius, color, lineWidth) {
    context.save();
    context.beginPath();
    context.arc(x1, y1, radius, 0, 2*Math.PI, false);
    context.fillStyle = color;
    context.fill();
    context.lineWidth = lineWidth;
    context.strokeStyle = '#003300';
    context.stroke();
    context.restore();
}

function drawBoard(board) {
    var rink = board.rink;
    var puck = board.puck;
    var goals = board.goals;

    // Draw the rink.
    drawPath(rink.vertices, "black", 3);

    // Draw the goals.
    var color;
    for (var i = 0; i < goals.length; i++) {
        color = kTeamColors[i]
        var goal = goals[i];
        drawPath(goal.outer_vertices.slice(0, -1), kTeamColors[i]);
        drawPath(goal.inner_vertices.slice(0, -1), "deeppink");
    }

    // Draw the puck.
    var position = puck.position;
    drawCircle(convert(position[0]), convert(position[1]), kScale*puck.radius, "green", 5);
}

function drawPath(path, color, lineWidth) {
    for (var i=0; i < path.length; i++) {
        var next_i = (i+1) % path.length;
        drawLine(convert(path[i][0]), convert(path[i][1]), convert(path[next_i][0]), convert(path[next_i][1]), color, lineWidth);
    }
}

function drawPlayers(players) {
    for (var i = 0; i < players.length; i++) {
        var player = players[i];

        var hull = player.hull;
        var wheels = player.wheels;
        var lidar_points = player.lidar_points;
        var lidar_categories = player.lidar_categories;
        var numAgent = player.numagent;
        var team = player.team;

        for (var j=0; j < hull.path.length; j++) {
            drawPath(hull.path[j], kTeamColors[team - 1], 3);
        }

        for (var j=0; j < wheels.length; j++) {
            drawPath(wheels[j].path, "red");
        }

        var color;
        for (var j=0; j < lidar_points.length; j++) {
            color = kLidarCategoryColors[lidar_categories[j]];
            drawLine(convert(lidar_points[j][0][0]), convert(lidar_points[j][0][1]),
                     convert(lidar_points[j][1][0]), convert(lidar_points[j][1][1]),
                     color, 1);
        }

        context.save();
        context.font = "12px Arial"
        context.fillText(team, convert(hull.position[0]), convert(hull.position[1]));
        context.fillText(numAgent, convert(hull.position[0]), 15 + convert(hull.position[1]));
        context.restore();
    }
}


function drawText(time, score, scored) {
    var scoreStr = score.join(" : ");
    context.save()
    context.font = "18px Arial"
    context.fillText("Time Remaining:", kTextStartPosition, 50);
    context.fillText(time, kDataStartPosition, 50);
    context.fillText("Score:", kTextStartPosition, 100);
    context.fillText(scoreStr, kDataStartPosition, 100);
    context.fillText("Just Scored:", kTextStartPosition, 150);
    context.fillText(scored, kDataStartPosition, 150);
    context.restore()
}

function convert(val) {
    return kScale*val + 500;
}


