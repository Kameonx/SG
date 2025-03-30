<!DOCTYPE html>
<html>
<head>
    <title>16-bit Sprite Generator</title>
    <style>
        body {
            background-color: #222;
            color: #eee;
            font-family: sans-serif;
            margin: 20px;
        }
        h1 {
            text-align: center;
            color: #fff;
        }
        form {
            display: flex;
            flex-direction: column;
            width: 320px;
            margin: 0 auto;
            gap: 15px;
        }
        select, button {
            padding: 10px;
            font-size: 16px;
            background-color: #444;
            color: #eee;
            border: 1px solid #777;
        }
    </style>
</head>
<body>
    <h1>16-bit Sprite Generator</h1>
    <form action="/generate" method="post">
        <select name="class">
            {% for c in classes %}
            <option value="{{c}}">{{c.title()}}</option>
            {% endfor %}
            <option value="Slime">Slime</option>
            <option value="Goblin">Goblin</option>
            <option value="Wolf">Wolf</option>
            <option value="Bear">Bear</option>
            <option value="Troll">Troll</option>
            <option value="Ogre">Ogre</option>
            <option value="Human Bandit Warrior">Human Bandit Warrior</option>
            <option value="Human Bandit Mage">Human Bandit Mage</option>
            <option value="Human Bandit Archer">Human Bandit Archer</option>
        </select>
        
        <select name="animation">
            {% for a in animations %}
            <option value="{{a}}">{{a.title()}}</option>
            {% endfor %}
            <option value="Dying">Dying</option>
        </select>
        
        <button type="submit">Generate Sprite!</button>
    </form>
</body>
</html>
